from __future__ import annotations

import json
import os
import secrets
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request

APP_DIR = Path(__file__).resolve().parent
REPO_DATA_DIR = APP_DIR.parent.parent / "Resource" / "Data"
DEFAULT_DATA_DIR = APP_DIR / "data"

DB_PATH = Path(os.getenv("GAME_SERVER_DB_PATH", str(DEFAULT_DATA_DIR / "game_server.db"))).expanduser()


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def parse_time(text: str) -> datetime:
    try:
        return datetime.strptime(text, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return datetime.min


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def normalize_users(raw: Any) -> list[dict[str, str]]:
    if isinstance(raw, dict) and isinstance(raw.get("users"), list):
        users = raw["users"]
    elif isinstance(raw, list):
        users = raw
    else:
        users = []

    normalized: list[dict[str, str]] = []
    for item in users:
        if not isinstance(item, dict):
            continue
        login_id = str(item.get("id", "")).strip()
        password = str(item.get("password", "")).strip()
        nickname = str(item.get("nickname", login_id)).strip() or login_id
        if not login_id or not password:
            continue
        normalized.append({"id": login_id, "password": password, "nickname": nickname})
    return normalized


def users_json_candidates() -> list[Path]:
    candidates: list[Path] = []

    env_path = os.getenv("USERS_JSON_PATH", "").strip()
    if env_path:
        candidates.append(Path(env_path).expanduser())

    candidates.append(DEFAULT_DATA_DIR / "users_seed.json")
    candidates.append(REPO_DATA_DIR / "users.json")

    unique: list[Path] = []
    seen: set[str] = set()
    for path in candidates:
        key = str(path.resolve()) if path.exists() else str(path)
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    return unique


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                nickname TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS game_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login_id TEXT NOT NULL,
                nickname TEXT NOT NULL,
                play_time TEXT NOT NULL,
                score INTEGER NOT NULL,
                filter_name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(login_id) REFERENCES users(id) ON DELETE RESTRICT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS result_shares (
                share_code TEXT PRIMARY KEY,
                result_id INTEGER NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(result_id) REFERENCES game_results(id) ON DELETE CASCADE
            )
            """
        )


def upsert_user(login_id: str, password: str, nickname: str) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO users(id, password, nickname, created_at, updated_at)
            VALUES(?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                password=excluded.password,
                nickname=excluded.nickname,
                updated_at=excluded.updated_at
            """,
            (login_id, password, nickname, now_str(), now_str()),
        )


def seed_users_from_sources() -> tuple[int, list[str]]:
    total = 0
    used_paths: list[str] = []

    for path in users_json_candidates():
        if not path.exists():
            continue

        try:
            raw = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            continue

        users = normalize_users(raw)
        if not users:
            continue

        for user in users:
            upsert_user(user["id"], user["password"], user["nickname"])
            total += 1

        used_paths.append(str(path))

    admin_id = os.getenv("ADMIN_LOGIN_ID", "").strip()
    admin_pw = os.getenv("ADMIN_PASSWORD", "").strip()
    admin_nickname = os.getenv("ADMIN_NICKNAME", admin_id).strip() or admin_id

    if admin_id and admin_pw:
        upsert_user(admin_id, admin_pw, admin_nickname)
        total += 1
        used_paths.append("ENV:ADMIN_LOGIN_ID")

    return total, used_paths


def create_share_code(length: int = 12) -> str:
    raw = secrets.token_urlsafe(length)
    return raw.replace("-", "").replace("_", "")[:length]


def get_user_by_id(login_id: str) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute("SELECT id, password, nickname FROM users WHERE id = ?", (login_id,)).fetchone()
    if row is None:
        return None
    return dict(row)


def get_latest_result_by_login_id(login_id: str) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT id, login_id, nickname, play_time, score, filter_name, created_at
            FROM game_results
            WHERE login_id = ?
            ORDER BY datetime(play_time) DESC, id DESC
            LIMIT 1
            """,
            (login_id,),
        ).fetchone()
    return dict(row) if row else None


def insert_game_result(login_id: str, nickname: str, play_time: str, score: int, filter_name: str) -> int:
    if parse_time(play_time) == datetime.min:
        play_time = now_str()

    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO game_results(login_id, nickname, play_time, score, filter_name, created_at)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            (login_id, nickname, play_time, score, filter_name, now_str()),
        )
        return int(cur.lastrowid)


def get_result_by_id(result_id: int) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT id, login_id, nickname, play_time, score, filter_name, created_at
            FROM game_results
            WHERE id = ?
            """,
            (result_id,),
        ).fetchone()
    return dict(row) if row else None


def insert_share(result_id: int, expire_minutes: int) -> tuple[str, str]:
    expire_minutes = max(1, min(expire_minutes, 60 * 24 * 30))
    expires_at = (datetime.now() + timedelta(minutes=expire_minutes)).strftime("%Y-%m-%d %H:%M:%S")

    with get_conn() as conn:
        while True:
            share_code = create_share_code(12)
            exists = conn.execute(
                "SELECT share_code FROM result_shares WHERE share_code = ?", (share_code,)
            ).fetchone()
            if exists is None:
                break

        conn.execute(
            """
            INSERT INTO result_shares(share_code, result_id, expires_at, created_at)
            VALUES(?, ?, ?, ?)
            """,
            (share_code, result_id, expires_at, now_str()),
        )

    return share_code, expires_at


def get_share_payload(share_code: str) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT
                s.share_code,
                s.expires_at,
                r.id AS result_id,
                r.login_id,
                r.nickname,
                r.play_time,
                r.score,
                r.filter_name
            FROM result_shares s
            JOIN game_results r ON r.id = s.result_id
            WHERE s.share_code = ?
            """,
            (share_code,),
        ).fetchone()

    if row is None:
        return None

    payload = dict(row)
    if parse_time(payload["expires_at"]) < datetime.now():
        return None
    return payload


def base_url() -> str:
    env_url = os.getenv("PUBLIC_BASE_URL", "").strip()
    if env_url:
        return env_url.rstrip("/")
    return request.host_url.rstrip("/")


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    init_db()
    seeded_count, seed_sources = seed_users_from_sources()
    if seeded_count:
        print(f"[INFO] users synced: {seeded_count}")
        print("[INFO] user sources:", ", ".join(seed_sources))
    else:
        print("[WARN] no users seeded; login API will fail until users are created.")

    @app.get("/")
    def index() -> Any:
        return jsonify(
            {
                "message": "OpenCV Game Result Server",
                "docs": [
                    "GET /api/health",
                    "POST /api/login",
                    "POST /api/results",
                    "GET /api/results/latest/<login_id>",
                    "POST /api/results/<result_id>/share",
                    "GET /api/share/<share_code>",
                    "GET /r/<share_code>",
                ],
            }
        )

    @app.get("/api/health")
    def api_health() -> Any:
        return jsonify({
            "ok": True,
            "time": now_str(),
            "db_path": str(DB_PATH),
            "render": bool(os.getenv("RENDER", "")),
        })

    @app.post("/api/login")
    def api_login() -> Any:
        body = request.get_json(silent=True) or {}
        login_id = str(body.get("id", "")).strip()
        password = str(body.get("password", "")).strip()

        if not login_id or not password:
            return jsonify({"ok": False, "error": "id and password are required"}), 400

        user = get_user_by_id(login_id)
        if user is None or user["password"] != password:
            return jsonify({"ok": False, "error": "invalid credentials"}), 401

        return jsonify({"ok": True, "id": user["id"], "nickname": user["nickname"]})

    @app.post("/api/results")
    def api_save_result() -> Any:
        body = request.get_json(silent=True) or {}

        login_id = str(body.get("login_id", "")).strip()
        nickname = str(body.get("nickname", "")).strip()
        play_time = str(body.get("play_time", "")).strip()
        filter_name = str(body.get("filter", "")).strip() or "BASIC"

        try:
            score = int(body.get("score", 0))
        except Exception:
            score = 0

        if not login_id:
            return jsonify({"ok": False, "error": "login_id is required"}), 400
        if not play_time:
            play_time = now_str()

        user = get_user_by_id(login_id)
        if user is None:
            return jsonify({"ok": False, "error": "unknown login_id"}), 404

        if not nickname:
            nickname = str(user["nickname"])

        result_id = insert_game_result(login_id, nickname, play_time, score, filter_name)
        return jsonify({"ok": True, "result_id": result_id})

    @app.get("/api/results/latest/<login_id>")
    def api_latest_result(login_id: str) -> Any:
        data = get_latest_result_by_login_id(login_id)
        if data is None:
            return jsonify({"ok": False, "error": "no result found"}), 404

        return jsonify(
            {
                "ok": True,
                "result": {
                    "result_id": data["id"],
                    "login_id": data["login_id"],
                    "nickname": data["nickname"],
                    "play_time": data["play_time"],
                    "score": data["score"],
                    "filter": data["filter_name"],
                },
            }
        )

    @app.post("/api/results/<int:result_id>/share")
    def api_create_share(result_id: int) -> Any:
        body = request.get_json(silent=True) or {}
        try:
            expire_minutes = int(body.get("expire_minutes", 60 * 24))
        except Exception:
            expire_minutes = 60 * 24

        result = get_result_by_id(result_id)
        if result is None:
            return jsonify({"ok": False, "error": "result_id not found"}), 404

        share_code, expires_at = insert_share(result_id, expire_minutes)
        share_url = f"{base_url()}/r/{share_code}"

        return jsonify(
            {
                "ok": True,
                "share_code": share_code,
                "share_url": share_url,
                "expires_at": expires_at,
            }
        )

    @app.get("/api/share/<share_code>")
    def api_share_json(share_code: str) -> Any:
        payload = get_share_payload(share_code)
        if payload is None:
            return jsonify({"ok": False, "error": "invalid or expired share code"}), 404

        return jsonify(
            {
                "ok": True,
                "result": {
                    "name": payload["nickname"],
                    "play_time": payload["play_time"],
                    "score": payload["score"],
                    "filter": payload["filter_name"],
                    "login_id": payload["login_id"],
                },
                "share_code": payload["share_code"],
                "expires_at": payload["expires_at"],
            }
        )

    @app.get("/r/<share_code>")
    def result_page(share_code: str) -> Any:
        payload = get_share_payload(share_code)
        if payload is None:
            return render_template(
                "result_view.html",
                title="Result Not Available",
                error="This result link is invalid or expired.",
                result=None,
            ), 404

        result = {
            "Name": payload["nickname"],
            "PlayTime": payload["play_time"],
            "Score": payload["score"],
            "Filter": payload["filter_name"],
            "LoginID": payload["login_id"],
            "ShareCode": payload["share_code"],
            "ExpiresAt": payload["expires_at"],
        }

        return render_template("result_view.html", title="Game Result", error="", result=result)

    return app


app = create_app()


if __name__ == "__main__":
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "5000"))
    app.run(host=host, port=port, debug=False)
