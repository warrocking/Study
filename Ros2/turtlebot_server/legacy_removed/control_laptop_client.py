import argparse
import json
import socket
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Union


SCRIPT_DIR = Path(__file__).resolve().parent

FLEET_JSON_VERSION = 4
FLEET_JSON_SCHEMA = "fleet_json_v0.4"
DEFAULT_AUTH_TOKEN = "team_demo_token"

ACTION_ALIASES = {
    "stop": "robot_stop",
}

FORCE_ALL_TARGET_ACTIONS = {
    "all_stop",
    "emergency_stop",
    "pause_all",
    "resume_all",
    "reset_all_jobs",
    "clear_emergency",
}

GROUP_ACTIONS = {
    "all_stop",
    "emergency_stop",
    "pause_all",
    "resume_all",
    "reset_all_jobs",
}

STATUS_ACTIONS = {
    "status_request",
    "robot_state_request",
    "job_status_request",
    "ping",
    "mapping_status",
    "map_status",
    "map_list",
    "nav_status",
}

MOVE_ACTIONS = {
    "move_forward",
    "move_backward",
    "turn_left",
    "turn_right",
    "custom_move",
}

TargetInput = Union[str, Sequence[str]]


DEFAULT_CONFIG: Dict[str, Any] = {
    "protocol_version": FLEET_JSON_VERSION,
    "server_ip": "127.0.0.1",
    "server_port": 4000,
    "timeout": 8.0,
    "auth_token": DEFAULT_AUTH_TOKEN,
    "user": "operator_1",
    "default_target": "tb3_3",
    "defaults": {
        "lx": 0.05,
        "az": 0.0,
        "turn_az": 0.5,
        "dur": 2.0,
        "hz": 10,
        "stop": True,
    },
}


class IdGenerator:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._seq_by_prefix: Dict[str, int] = {}

    def next(self, prefix: str, label: str = "", seq_width: int = 6) -> str:
        clean_prefix = clean_id_label(prefix) or "ID"
        clean_label = clean_id_label(label)
        seq_key = f"{clean_prefix}:{clean_label}"
        with self._lock:
            self._seq_by_prefix[seq_key] = self._seq_by_prefix.get(seq_key, 0) + 1
            seq = self._seq_by_prefix[seq_key]
        date_text = datetime.now().strftime("%Y%m%d")
        if clean_label:
            return f"{clean_prefix}_{date_text}_{clean_label}_{seq:0{seq_width}d}"
        return f"{clean_prefix}_{date_text}_{seq:0{seq_width}d}"


ids = IdGenerator()


def now_ts() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def clean_id_label(label: str) -> str:
    return "_".join("".join(ch if ch.isalnum() else "_" for ch in str(label).upper()).split("_"))


def normalize_action(action: str) -> str:
    action_text = str(action).strip()
    return ACTION_ALIASES.get(action_text, action_text)


def make_target_list(target: TargetInput) -> list[str]:
    if isinstance(target, str):
        target_text = target.strip()
        if "," in target_text:
            return [item.strip() for item in target_text.split(",") if item.strip()]
        return [target_text] if target_text else ["tb3_3"]

    targets = [str(item).strip() for item in target if str(item).strip()]
    return targets or ["tb3_3"]


def make_target_scope(targets: list[str]) -> str:
    if targets == ["all"] or "all" in targets:
        return "all"
    if len(targets) > 1:
        return "multi"
    return "single"


def default_timeout_sec(action: str) -> float:
    if action in {"all_stop", "emergency_stop", "robot_stop"}:
        return 3.0
    if action in STATUS_ACTIONS:
        return 3.0
    return 5.0


def make_expects(action: str) -> Dict[str, Any]:
    return {
        "response_type": "sync",
        "status_followup": action in {"all_stop", "emergency_stop", "robot_stop"},
    }


def pretty_json(data: Dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def send_json(sock: socket.socket, data: Dict[str, Any]) -> None:
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    sock.sendall((text + "\n").encode("utf-8"))


def recv_json_line(file_obj) -> Optional[Dict[str, Any]]:
    line = file_obj.readline()
    if line == "":
        return None
    return json.loads(line)


def deep_update(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_update(result[key], value)
        else:
            result[key] = value
    return result


def load_json_file(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return dict(default)
    try:
        with path.open("r", encoding="utf-8") as f:
            loaded = json.load(f)
        if isinstance(loaded, dict):
            return deep_update(default, loaded)
    except Exception:
        pass
    return dict(default)


def make_operator_request(
    target: TargetInput,
    action: str,
    params: Optional[Dict[str, Any]] = None,
    user: str = "operator_1",
    button: str = "cli",
    auth_token: str = DEFAULT_AUTH_TOKEN,
    timeout_sec: Optional[float] = None,
    source: str = "control_ui",
    dest: str = "fleet_server",
) -> Dict[str, Any]:
    canonical_action = normalize_action(action)
    targets = ["all"] if canonical_action in FORCE_ALL_TARGET_ACTIONS else make_target_list(target)
    target_scope = make_target_scope(targets)
    target_label = "all" if target_scope == "all" else "_".join(targets)
    command_id = ids.next("CMD", f"{canonical_action}_{target_label}")
    group_id = ids.next("GRP", canonical_action) if canonical_action in GROUP_ACTIONS else None

    command_params = dict(params or {})
    if canonical_action == "all_stop":
        command_params.setdefault("reason", "operator_all_stop")
    elif canonical_action in {"robot_stop", "emergency_stop"}:
        command_params.setdefault("reason", f"operator_{canonical_action}")
    elif canonical_action in MOVE_ACTIONS:
        command_params.setdefault("stop", True)

    return {
        "v": FLEET_JSON_VERSION,
        "mt": "operator_request",
        "msg_id": ids.next("MSG", "operator_request"),
        "ts": now_ts(),
        "source": source,
        "dest": dest,
        "schema": FLEET_JSON_SCHEMA,
        "auth": {
            "token": auth_token,
        },
        "user": user,
        "command": {
            "command_id": command_id,
            "group_id": group_id,
            "job_id": None,
            "command_seq": None,
            "command_revision": 0,
            "action": canonical_action,
            "target_scope": target_scope,
            "targets": targets,
            "params": command_params,
            "expects": make_expects(canonical_action),
            "timeout_sec": float(timeout_sec if timeout_sec is not None else default_timeout_sec(canonical_action)),
        },
        "ui_context": {
            "client": "control_laptop_client.py",
            "screen": "external_ui_or_cli",
            "button": button,
        },
    }


class ControlServerClient:
    def __init__(
        self,
        server_ip: str,
        server_port: int,
        timeout: float = 8.0,
        auth_token: str = DEFAULT_AUTH_TOKEN,
        source: str = "control_ui",
        dest: str = "fleet_server",
    ) -> None:
        self.server_ip = server_ip
        self.server_port = int(server_port)
        self.timeout = float(timeout)
        self.auth_token = auth_token
        self.source = source
        self.dest = dest

    def send_operator_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        with socket.create_connection((self.server_ip, self.server_port), timeout=self.timeout) as sock:
            sock.settimeout(self.timeout)
            send_json(sock, request)
            file_obj = sock.makefile("r", encoding="utf-8")
            response = recv_json_line(file_obj)
            if response is None:
                raise RuntimeError("Server closed connection without response")
            return response

    def make_request(
        self,
        target: TargetInput,
        action: str,
        params: Optional[Dict[str, Any]] = None,
        user: str = "operator_1",
        button: str = "cli",
        timeout_sec: Optional[float] = None,
    ) -> Dict[str, Any]:
        return make_operator_request(
            target,
            action,
            params,
            user=user,
            button=button,
            auth_token=self.auth_token,
            timeout_sec=timeout_sec,
            source=self.source,
            dest=self.dest,
        )

    def request(
        self,
        target: TargetInput,
        action: str,
        params: Optional[Dict[str, Any]] = None,
        user: str = "operator_1",
    ) -> Dict[str, Any]:
        req = self.make_request(target, action, params, user=user, button=str(action))
        return self.send_operator_request(req)

    def move_forward(self, target: str, params: Optional[Dict[str, Any]] = None, user: str = "operator_1") -> Dict[str, Any]:
        req = self.make_request(target, "move_forward", params, user=user, button="move_forward")
        return self.send_operator_request(req)

    def move_backward(self, target: str, params: Optional[Dict[str, Any]] = None, user: str = "operator_1") -> Dict[str, Any]:
        req = self.make_request(target, "move_backward", params, user=user, button="move_backward")
        return self.send_operator_request(req)

    def turn_left(self, target: str, params: Optional[Dict[str, Any]] = None, user: str = "operator_1") -> Dict[str, Any]:
        req = self.make_request(target, "turn_left", params, user=user, button="turn_left")
        return self.send_operator_request(req)

    def turn_right(self, target: str, params: Optional[Dict[str, Any]] = None, user: str = "operator_1") -> Dict[str, Any]:
        req = self.make_request(target, "turn_right", params, user=user, button="turn_right")
        return self.send_operator_request(req)

    def custom_move(self, target: str, params: Dict[str, Any], user: str = "operator_1") -> Dict[str, Any]:
        req = self.make_request(target, "custom_move", params, user=user, button="custom_move")
        return self.send_operator_request(req)

    def stop(self, target: str, user: str = "operator_1") -> Dict[str, Any]:
        req = self.make_request(target, "stop", {}, user=user, button="stop")
        return self.send_operator_request(req)

    def all_stop(self, user: str = "operator_1") -> Dict[str, Any]:
        req = self.make_request("all", "all_stop", {}, user=user, button="all_stop")
        return self.send_operator_request(req)

    def status_request(self, user: str = "operator_1") -> Dict[str, Any]:
        req = self.make_request("all", "status_request", {}, user=user, button="status_request")
        return self.send_operator_request(req)

    def robot_state_request(self, target: TargetInput = "all", user: str = "operator_1") -> Dict[str, Any]:
        req = self.make_request(target, "robot_state_request", {}, user=user, button="robot_state_request")
        return self.send_operator_request(req)

    def job_status_request(
        self,
        target: TargetInput = "all",
        job_id: Optional[str] = None,
        user: str = "operator_1",
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if job_id:
            params["job_id"] = job_id
        req = self.make_request(target, "job_status_request", params, user=user, button="job_status_request")
        return self.send_operator_request(req)

    def ping(self, target: TargetInput = "all", user: str = "operator_1") -> Dict[str, Any]:
        req = self.make_request(target, "ping", {}, user=user, button="ping")
        return self.send_operator_request(req)


def load_config(path: Path) -> Dict[str, Any]:
    return load_json_file(path, DEFAULT_CONFIG)


def print_menu(target: str) -> None:
    print()
    print("========================================")
    print("Control Laptop Communication Client")
    print("========================================")
    print(f"current target: {target}")
    print("1. move_forward")
    print("2. move_backward")
    print("3. turn_left")
    print("4. turn_right")
    print("5. stop")
    print("6. ALL STOP")
    print("7. status_request")
    print("8. custom_move")
    print("9. change target")
    print("q. quit")
    print()


def ask_float(label: str, default: float) -> float:
    text = input(f"{label} [{default}] : ").strip()
    if not text:
        return float(default)
    return float(text)


def ask_int(label: str, default: int) -> int:
    text = input(f"{label} [{default}] : ").strip()
    if not text:
        return int(default)
    return int(text)


def run_interactive(client: ControlServerClient, config: Dict[str, Any]) -> None:
    user = str(config.get("user", "operator_1"))
    target = str(config.get("default_target", "tb3_3"))
    defaults = config.get("defaults", {})

    print(f"[CONNECT TARGET] {client.server_ip}:{client.server_port}")
    print(f"[PROTOCOL] Fleet JSON v{FLEET_JSON_VERSION} ({FLEET_JSON_SCHEMA})")
    print("The UI/UX owner can later import ControlServerClient from this file.")

    while True:
        print_menu(target)
        choice = input("select > ").strip().lower()
        if choice == "q":
            break

        try:
            if choice == "1":
                response = client.move_forward(target, {}, user=user)
            elif choice == "2":
                response = client.move_backward(target, {}, user=user)
            elif choice == "3":
                response = client.turn_left(target, {}, user=user)
            elif choice == "4":
                response = client.turn_right(target, {}, user=user)
            elif choice == "5":
                response = client.stop(target, user=user)
            elif choice == "6":
                response = client.all_stop(user=user)
            elif choice == "7":
                response = client.status_request(user=user)
            elif choice == "8":
                params = {
                    "lx": ask_float("lx", float(defaults.get("lx", 0.05))),
                    "az": ask_float("az", float(defaults.get("az", 0.0))),
                    "dur": ask_float("dur", float(defaults.get("dur", 2.0))),
                    "hz": ask_int("hz", int(defaults.get("hz", 10))),
                    "stop": True,
                }
                response = client.custom_move(target, params, user=user)
            elif choice == "9":
                new_target = input("target [tb3_1/tb3_2/tb3_3/all] : ").strip()
                if new_target:
                    target = new_target
                continue
            else:
                print("[WARN] unknown menu")
                continue

            print()
            print("[SERVER RESPONSE]")
            print(pretty_json(response))
        except Exception as exc:
            print(f"[ERROR] request failed: {exc}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Control laptop communication client")
    parser.add_argument("--config", default=str(SCRIPT_DIR / "control_client_config.json"))
    parser.add_argument("--server-ip", default="")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--token", default="")
    parser.add_argument("--target", default="")
    parser.add_argument("--action", default="", help="Run one action and exit")
    parser.add_argument("--dry-run", action="store_true", help="Print the v4 operator_request without sending it")
    parser.add_argument("--lx", type=float, default=None)
    parser.add_argument("--az", type=float, default=None)
    parser.add_argument("--dur", type=float, default=None)
    parser.add_argument("--hz", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(Path(args.config))

    server_ip = args.server_ip or str(config.get("server_ip", "127.0.0.1"))
    server_port = args.port or int(config.get("server_port", 4000))
    timeout = float(config.get("timeout", 8.0))
    auth_token = args.token or str(config.get("auth_token", DEFAULT_AUTH_TOKEN))
    client = ControlServerClient(server_ip, server_port, timeout=timeout, auth_token=auth_token)

    if not args.action:
        run_interactive(client, config)
        return

    target = args.target or str(config.get("default_target", "tb3_3"))
    user = str(config.get("user", "operator_1"))
    params: Dict[str, Any] = {}
    for key in ["lx", "az", "dur", "hz"]:
        value = getattr(args, key)
        if value is not None:
            params[key] = value

    request = client.make_request(target, args.action, params, user=user, button=f"cli_{args.action}")
    if args.dry_run:
        print(pretty_json(request))
        return
    response = client.send_operator_request(request)
    print(pretty_json(response))


if __name__ == "__main__":
    main()
