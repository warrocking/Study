from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

try:
    import qrcode
except Exception:
    qrcode = None

ROOT_DIR = Path(__file__).resolve().parents[2]
LOCAL_RESULT_DIR = ROOT_DIR / "Resource" / "Data" / "GameResult"
OUTPUT_DIR = ROOT_DIR / "Resource" / "Data" / "ServerShareQR"
DEFAULT_SERVER = "http://127.0.0.1:5000"


def find_latest_result_file() -> Path | None:
    files = sorted(LOCAL_RESULT_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def post_json(url: str, payload: dict) -> dict:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        text = resp.read().decode("utf-8")
    return json.loads(text)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def make_result_payload(raw: dict) -> dict:
    return {
        "login_id": str(raw.get("LoginID", "")).strip(),
        "nickname": str(raw.get("Name", "")).strip(),
        "play_time": str(raw.get("PlayTime", "")).strip(),
        "score": int(raw.get("Score", 0)),
        "filter": str(raw.get("Filter", "BASIC")).strip() or "BASIC",
    }


def main() -> None:
    server_base = os.getenv("GAME_SERVER_URL", DEFAULT_SERVER).rstrip("/")
    expire_minutes = int(os.getenv("SHARE_EXPIRE_MINUTES", "1440"))

    latest_file = find_latest_result_file()
    if latest_file is None:
        print(f"[ERROR] No local result file found: {LOCAL_RESULT_DIR}")
        return

    raw = read_json(latest_file)
    payload = make_result_payload(raw)

    if not payload["login_id"]:
        print("[ERROR] LoginID is empty in latest result JSON.")
        return

    try:
        save_resp = post_json(f"{server_base}/api/results", payload)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        print(f"[ERROR] Save failed ({exc.code}): {detail}")
        return
    except Exception as exc:
        print(f"[ERROR] Save request failed: {exc}")
        return

    if not save_resp.get("ok"):
        print(f"[ERROR] Save API failed: {save_resp}")
        return

    result_id = int(save_resp["result_id"])

    try:
        share_resp = post_json(
            f"{server_base}/api/results/{result_id}/share",
            {"expire_minutes": expire_minutes},
        )
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        print(f"[ERROR] Share failed ({exc.code}): {detail}")
        return
    except Exception as exc:
        print(f"[ERROR] Share request failed: {exc}")
        return

    if not share_resp.get("ok"):
        print(f"[ERROR] Share API failed: {share_resp}")
        return

    share_url = str(share_resp["share_url"])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "latest_share_url.txt").write_text(share_url, encoding="utf-8")
    (OUTPUT_DIR / "latest_uploaded_result.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    if qrcode is not None:
        img = qrcode.make(share_url)
        img.save(OUTPUT_DIR / "latest_share_qr.png")
        print(f"[OK] QR image: {OUTPUT_DIR / 'latest_share_qr.png'}")
    else:
        print("[WARN] qrcode package not found, skip QR image")

    print(f"[OK] source result: {latest_file}")
    print(f"[OK] share url: {share_url}")
    print(f"[OK] url file: {OUTPUT_DIR / 'latest_share_url.txt'}")


if __name__ == "__main__":
    main()
