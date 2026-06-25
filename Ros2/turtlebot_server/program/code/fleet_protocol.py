import json
import socket
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple


JSONDict = Dict[str, Any]

FLEET_JSON_VERSION = 4
FLEET_JSON_SCHEMA = "fleet_json_v0.4"
FLEET_JSON_VERSION_V5 = 5
FLEET_JSON_SCHEMA_V5 = "fleet_json_v0.5.1"
FLEET_JSON_VERSION_V6 = 6
FLEET_JSON_SCHEMA_V6 = "fleet_json_v0.6"
FLEET_JSON_SCHEMA_V5_COMPAT = {
    "fleet_json_v0.5",
    FLEET_JSON_SCHEMA_V5,
    FLEET_JSON_SCHEMA_V6,
}
FLEET_JSON_SCHEMA_V6_COMPAT = {
    "fleet_json_v0.5",
    FLEET_JSON_SCHEMA_V5,
    FLEET_JSON_SCHEMA_V6,
}

FLEET_ENDPOINTS = {
    "control_ui",
    "fleet_server",
    "robot_command_client",
    "robot_gateway_client",
}

FLEET_MESSAGE_TYPES = {
    "operator_request",
    "operator_response",
    "server_command",
    "agent_result",
    "heartbeat_request",
    "heartbeat_response",
    "state_report",
    "file_sync_report",
    "error_report",
}

FLEET_MESSAGE_TYPES_V5 = {
    "control_health_request",
    "control_health_response",
    "operator_request",
    "operator_response",
    "control_command_request",
    "control_data_request",
    "control_data_response",
    "server_command",
    "agent_result",
    "client_heartbeat_request",
    "client_heartbeat_response",
    "client_data_prepare_request",
    "client_data_prepare_response",
    "client_data_result_report",
    "transfer_plan",
    "transfer_result",
    "emergency_event",
    "state_snapshot",
    "log_event",
    "error_report",
}

FLEET_ACTIONS = {
    "status_request",
    "robot_state_request",
    "job_status_request",
    "ping",
    "emergency_stop",
    "all_stop",
    "robot_stop",
    "stop",
    "pause_all",
    "pause_robot",
    "resume_all",
    "resume_robot",
    "cancel_job",
    "reset_all_jobs",
    "clear_error",
    "clear_emergency",
    "move_forward",
    "move_backward",
    "turn_left",
    "turn_right",
    "custom_move",
    "start_mapping",
    "stop_mapping",
    "mapping_status",
    "save_map",
    "rsync_map",
    "image_request",
    "image_view_closed",
    "file_cleanup_report",
    "map_status",
    "map_list",
    "map_image_select",
    "nav_goal",
    "nav_status",
    "nav_cancel",
}

ACTION_ALIASES = {
    "stop": "robot_stop",
}

RESULT_CODES_OK = {
    "R_ACCEPTED",
    "R_STARTED",
    "R_RUNNING",
    "R_DONE",
    "R_STATUS",
    "R_PONG",
    "R_STOPPED",
    "R_PAUSED",
    "R_RESUMED",
    "R_CANCELED",
    "R_MAP_LOCAL_SAVED",
    "R_MAP_SYNCING",
    "R_FILE_SYNC_REPORTED",
    "R_MAP_READY",
    "R_PARTIAL_SUCCESS",
    "R_HEALTH_OK",
    "R_HEALTH_WARN",
    "R_CLIENT_TCP_CONNECTED",
    "R_CLIENT_ALIVE",
    "R_TRANSFER_DONE",
    "R_SKIPPED",
}

RESULT_CODES_ERROR = {
    "E_BAD_REQUEST",
    "E_AUTH_FAILED",
    "E_DUPLICATE_COMMAND",
    "E_OUTDATED_COMMAND",
    "E_JOB_ALREADY_CANCELED",
    "E_UNKNOWN_ACTION",
    "E_MODE_BLOCKED",
    "E_ROBOT_BUSY",
    "E_TARGET_INVALID",
    "E_AGENT_DISCONNECTED",
    "E_TIMEOUT",
    "E_MAPPING_CONDITION",
    "E_NAV_CONDITION",
    "E_FILE_SYNC_FAILED",
    "E_MAP_NOT_READY",
    "E_SYSTEM_EMERGENCY",
    "E_STATE_MISMATCH",
    "E_RESULT_MISMATCH",
    "E_INTERNAL_ERROR",
}

UI_MODES = {"OFFLINE", "READY", "BUSY_QUEUEABLE", "BUSY_BLOCKED", "PAUSED", "EMERGENCY"}
OPERATING_MODES = {
    "STARTUP",
    "AUTO",
    "MANUAL",
    "MAPPING",
    "NAVIGATION",
    "PAUSED",
    "SERVICE",
    "ERROR",
    "EMERGENCY",
    "SHUTDOWN",
}
ROBOT_STATES = {
    "IDLE",
    "MOVING",
    "MAPPING",
    "NAVIGATING",
    "SAVING_MAP",
    "SYNCING_FILE",
    "STOPPED",
    "PAUSED",
    "ERROR",
    "DISCONNECTED",
    "EMERGENCY",
}
JOB_STATES = {
    "NONE",
    "PENDING",
    "ACCEPTED",
    "QUEUED",
    "RUNNING",
    "PAUSING",
    "PAUSED",
    "RESUMING",
    "STOPPING",
    "DONE",
    "FAILED",
    "CANCELING",
    "CANCELED",
    "ABORTED",
    "REJECTED",
}
ACCEPT_STATES = {"ACCEPTING", "QUEUEABLE", "BLOCKED"}
GLOBAL_STATES = {"NORMAL", "PAUSED_ALL", "EMERGENCY", "SERVICE", "SHUTDOWN"}

BLOCKING_TYPES = {"NONE", "SOFT", "HARD", "SINGLE"}
INTERRUPT_POLICIES = {"status_only", "reject_if_busy", "queue_if_busy", "replace_same_job", "interrupt_current"}
COMMAND_TYPES = {"emergency", "control", "immediate", "normal", "background"}
TARGET_SCOPES = {"single", "multi", "all"}


class ProtocolError(Exception):
    """Raised when a received message does not follow the fleet protocol."""


def now_ts() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def safe_time_string() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def compact_json(data: JSONDict) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def pretty_json(data: JSONDict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def send_json(sock: socket.socket, data: JSONDict) -> None:
    payload = compact_json(data) + "\n"
    sock.sendall(payload.encode("utf-8"))


def recv_json_line(file_obj, max_chars: int = 262144) -> Optional[JSONDict]:
    line = file_obj.readline(max_chars + 1)
    if line == "":
        return None
    if len(line) > max_chars:
        raise ProtocolError(f"JSON line is too large: {len(line)} chars")
    try:
        return json.loads(line)
    except json.JSONDecodeError as exc:
        raise ProtocolError(f"Bad JSON: {exc}") from exc


def deep_update(base: JSONDict, override: JSONDict) -> JSONDict:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_update(result[key], value)
        else:
            result[key] = value
    return result


def load_json_file(path: Path, default: JSONDict) -> JSONDict:
    if not path.exists():
        save_json_file(path, default)
        return dict(default)
    try:
        with path.open("r", encoding="utf-8") as f:
            loaded = json.load(f)
        if isinstance(loaded, dict):
            return deep_update(default, loaded)
    except Exception:
        pass
    return dict(default)


def save_json_file(path: Path, data: JSONDict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_json_log(base_dir: Path, category: str, prefix: str, data: JSONDict) -> Tuple[Path, Path]:
    folder = base_dir / category
    folder.mkdir(parents=True, exist_ok=True)
    history_path = folder / f"{prefix}_{safe_time_string()}.json"
    latest_path = folder / f"latest_{prefix}.json"
    save_json_file(history_path, data)
    save_json_file(latest_path, data)
    return history_path, latest_path


class IdGenerator:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._seq_by_prefix: Dict[str, int] = {}

    def next(self, prefix: str, label: str = "") -> str:
        with self._lock:
            self._seq_by_prefix[prefix] = self._seq_by_prefix.get(prefix, 0) + 1
            seq = self._seq_by_prefix[prefix]
        date_text = datetime.now().strftime("%Y%m%d")
        if label:
            clean_label = "".join(ch for ch in label.upper() if ch.isalnum() or ch == "_")
            return f"{prefix}{date_text}_{clean_label}_{seq:04d}"
        return f"{prefix}{date_text}_{seq:04d}"


_v4_id_lock = threading.Lock()
_v4_seq_by_prefix: Dict[str, int] = {}


def clean_id_label(label: str) -> str:
    return "_".join("".join(ch if ch.isalnum() else "_" for ch in label.upper()).split("_"))


def make_fleet_id(prefix: str, label: str = "", seq_width: int = 6) -> str:
    clean_prefix = clean_id_label(prefix) or "ID"
    clean_label = clean_id_label(label)
    seq_key = f"{clean_prefix}:{clean_label}"
    with _v4_id_lock:
        _v4_seq_by_prefix[seq_key] = _v4_seq_by_prefix.get(seq_key, 0) + 1
        seq = _v4_seq_by_prefix[seq_key]
    date_text = datetime.now().strftime("%Y%m%d")
    if clean_label:
        return f"{clean_prefix}_{date_text}_{clean_label}_{seq:0{seq_width}d}"
    return f"{clean_prefix}_{date_text}_{seq:0{seq_width}d}"


def make_msg_id(prefix: str = "MSG", label: str = "") -> str:
    return make_fleet_id(prefix, label)


def make_command_id(prefix: str = "CMD", label: str = "") -> str:
    return make_fleet_id(prefix, label)


def make_group_id(label: str = "") -> str:
    return make_fleet_id("GRP", label)


def make_job_id(label: str = "") -> str:
    return make_fleet_id("JOB", label)


def error_entry(code: str, msg: str, where: str, detail: Optional[JSONDict] = None) -> JSONDict:
    err: JSONDict = {
        "code": code,
        "msg": msg,
        "where": where,
    }
    if detail is not None:
        err["detail"] = detail
    return err


def required_fields(data: JSONDict, fields: Iterable[str]) -> Optional[str]:
    for field in fields:
        if field not in data:
            return field
    return None


def normalize_action(action: Any) -> str:
    if action is None:
        return ""
    action_text = str(action).strip()
    return ACTION_ALIASES.get(action_text, action_text)


def is_known_action(action: str, *, allow_alias: bool = True) -> bool:
    if action in FLEET_ACTIONS:
        return True
    if allow_alias and action in ACTION_ALIASES:
        return True
    return False


def make_common_message(
    mt: str,
    source: str,
    dest: str,
    msg_id: Optional[str] = None,
    ts: Optional[str] = None,
) -> JSONDict:
    return {
        "v": FLEET_JSON_VERSION,
        "mt": mt,
        "msg_id": msg_id or make_msg_id("MSG", mt),
        "ts": ts or now_ts(),
        "source": source,
        "dest": dest,
        "schema": FLEET_JSON_SCHEMA,
    }


def make_common_message_v5(
    mt: str,
    source: str,
    dest: str,
    msg_id: Optional[str] = None,
    ts: Optional[str] = None,
) -> JSONDict:
    return {
        "v": FLEET_JSON_VERSION_V5,
        "mt": mt,
        "msg_id": msg_id or make_msg_id("MSG", mt),
        "ts": ts or now_ts(),
        "source": source,
        "dest": dest,
        "schema": FLEET_JSON_SCHEMA_V5,
    }


def validate_common_fields(obj: JSONDict, expected_mt: Optional[str] = None) -> Tuple[bool, str, str]:
    if not isinstance(obj, dict):
        return False, "E_BAD_REQUEST", "message must be a JSON object"

    missing = required_fields(obj, ["v", "mt", "msg_id", "ts", "source", "dest", "schema"])
    if missing:
        return False, "E_BAD_REQUEST", f"Missing common field: {missing}"

    if obj.get("v") != FLEET_JSON_VERSION:
        return False, "E_BAD_REQUEST", f"v must be {FLEET_JSON_VERSION}"

    if obj.get("schema") != FLEET_JSON_SCHEMA:
        return False, "E_BAD_REQUEST", f"schema must be {FLEET_JSON_SCHEMA}"

    mt = obj.get("mt")
    if mt not in FLEET_MESSAGE_TYPES:
        return False, "E_BAD_REQUEST", f"unknown mt: {mt}"

    if expected_mt is not None and mt != expected_mt:
        return False, "E_BAD_REQUEST", f"mt must be {expected_mt}"

    source = obj.get("source")
    if source not in FLEET_ENDPOINTS:
        return False, "E_BAD_REQUEST", f"unknown source: {source}"

    dest = obj.get("dest")
    if dest not in FLEET_ENDPOINTS:
        return False, "E_BAD_REQUEST", f"unknown dest: {dest}"

    return True, "R_ACCEPTED", "OK"


def validate_common_fields_v5(obj: JSONDict, expected_mt: Optional[str] = None) -> Tuple[bool, str, str]:
    if not isinstance(obj, dict):
        return False, "E_BAD_REQUEST", "message must be a JSON object"

    missing = required_fields(obj, ["v", "mt", "msg_id", "ts", "source", "dest", "schema"])
    if missing:
        return False, "E_BAD_REQUEST", f"Missing common field: {missing}"

    if obj.get("v") not in {FLEET_JSON_VERSION_V5, FLEET_JSON_VERSION_V6}:
        return False, "E_BAD_REQUEST", f"v must be {FLEET_JSON_VERSION_V5} or {FLEET_JSON_VERSION_V6}"

    if obj.get("schema") not in FLEET_JSON_SCHEMA_V5_COMPAT:
        allowed = ", ".join(sorted(FLEET_JSON_SCHEMA_V5_COMPAT))
        return False, "E_BAD_REQUEST", f"schema must be one of: {allowed}"

    mt = obj.get("mt")
    if mt not in FLEET_MESSAGE_TYPES_V5:
        return False, "E_BAD_REQUEST", f"unknown mt: {mt}"

    if expected_mt is not None and mt != expected_mt:
        return False, "E_BAD_REQUEST", f"mt must be {expected_mt}"

    source = obj.get("source")
    if source not in FLEET_ENDPOINTS:
        return False, "E_BAD_REQUEST", f"unknown source: {source}"

    dest = obj.get("dest")
    if dest not in FLEET_ENDPOINTS:
        return False, "E_BAD_REQUEST", f"unknown dest: {dest}"

    return True, "R_ACCEPTED", "OK"


def validate_auth(obj: JSONDict, require_auth: bool, expected_token: str) -> Tuple[bool, str, str]:
    if not require_auth:
        return True, "R_ACCEPTED", "OK"

    auth = obj.get("auth")
    if not isinstance(auth, dict):
        return False, "E_AUTH_FAILED", "auth object is required"

    token = auth.get("token")
    if token != expected_token:
        return False, "E_AUTH_FAILED", "invalid auth token"

    return True, "R_ACCEPTED", "OK"


def validate_operator_request_v4(req: JSONDict) -> Tuple[bool, str, str]:
    ok, code, msg = validate_common_fields(req, expected_mt="operator_request")
    if not ok:
        return ok, code, msg

    missing = required_fields(req, ["auth", "user", "command"])
    if missing:
        return False, "E_BAD_REQUEST", f"Missing operator_request.{missing}"

    command = req.get("command")
    if not isinstance(command, dict):
        return False, "E_BAD_REQUEST", "operator_request.command must be an object"

    missing_command = required_fields(
        command,
        [
            "command_id",
            "command_revision",
            "action",
            "target_scope",
            "targets",
            "params",
            "timeout_sec",
        ],
    )
    if missing_command:
        return False, "E_BAD_REQUEST", f"Missing command.{missing_command}"

    action = str(command.get("action", ""))
    if not is_known_action(action):
        return False, "E_UNKNOWN_ACTION", f"unknown action: {action}"

    target_scope = command.get("target_scope")
    if target_scope not in {"single", "multi", "all"}:
        return False, "E_TARGET_INVALID", "target_scope must be single, multi, or all"

    targets = command.get("targets")
    if not isinstance(targets, list) or not targets:
        return False, "E_TARGET_INVALID", "targets must be a non-empty array"

    if not isinstance(command.get("params"), dict):
        return False, "E_BAD_REQUEST", "command.params must be an object"

    expects = command.get("expects", {})
    if expects is not None and not isinstance(expects, dict):
        return False, "E_BAD_REQUEST", "command.expects must be an object if present"

    return True, "R_ACCEPTED", "OK"


def validate_control_health_request_v5(req: JSONDict) -> Tuple[bool, str, str]:
    ok, code, msg = validate_common_fields_v5(req, expected_mt="control_health_request")
    if not ok:
        return ok, code, msg
    request = req.get("request", {})
    if request is not None and not isinstance(request, dict):
        return False, "E_BAD_REQUEST", "control_health_request.request must be an object"
    return True, "R_ACCEPTED", "OK"


def validate_operator_request_v5(req: JSONDict) -> Tuple[bool, str, str]:
    ok, code, msg = validate_common_fields_v5(req, expected_mt="operator_request")
    if not ok:
        return ok, code, msg

    missing = required_fields(req, ["command"])
    if missing:
        return False, "E_BAD_REQUEST", f"Missing operator_request.{missing}"

    command = req.get("command")
    if not isinstance(command, dict):
        return False, "E_BAD_REQUEST", "operator_request.command must be an object"

    missing_command = required_fields(
        command,
        [
            "command_id",
            "command_revision",
            "action",
            "target_scope",
            "targets",
            "params",
            "timeout_sec",
        ],
    )
    if missing_command:
        return False, "E_BAD_REQUEST", f"Missing command.{missing_command}"

    action = str(command.get("action", ""))
    if not is_known_action(action):
        return False, "E_UNKNOWN_ACTION", f"unknown action: {action}"

    target_scope = command.get("target_scope")
    if target_scope not in TARGET_SCOPES:
        return False, "E_TARGET_INVALID", "target_scope must be single, multi, or all"

    targets = command.get("targets")
    if not isinstance(targets, list) or not targets:
        return False, "E_TARGET_INVALID", "targets must be a non-empty array"

    if not isinstance(command.get("params"), dict):
        return False, "E_BAD_REQUEST", "command.params must be an object"

    return True, "R_ACCEPTED", "OK"


def validate_control_command_request_v5(req: JSONDict) -> Tuple[bool, str, str]:
    ok, code, msg = validate_common_fields_v5(req, expected_mt="control_command_request")
    if not ok:
        return ok, code, msg
    command = req.get("command")
    request = req.get("request")
    if not isinstance(command, dict) and not isinstance(request, dict):
        return False, "E_BAD_REQUEST", "control_command_request requires command or request object"
    return True, "R_ACCEPTED", "OK"


def validate_control_data_request_v5(req: JSONDict) -> Tuple[bool, str, str]:
    ok, code, msg = validate_common_fields_v5(req, expected_mt="control_data_request")
    if not ok:
        return ok, code, msg
    request = req.get("request")
    if not isinstance(request, dict):
        return False, "E_BAD_REQUEST", "control_data_request.request must be an object"
    data_type = request.get("data_type")
    if data_type not in {"image", "map", "log"}:
        return False, "E_BAD_REQUEST", "request.data_type must be image, map, or log"
    return True, "R_ACCEPTED", "OK"


def validate_server_command_v5(cmd: JSONDict) -> Tuple[bool, str, str]:
    ok, code, msg = validate_common_fields_v5(cmd, expected_mt="server_command")
    if not ok:
        return ok, code, msg

    command = cmd.get("command")
    if not isinstance(command, dict):
        return False, "E_BAD_REQUEST", "server_command.command must be an object"

    missing_command = required_fields(
        command,
        [
            "command_id",
            "command_revision",
            "op",
            "server_priority",
            "blocking_type",
            "interrupt_policy",
            "robot_id",
            "ros",
            "params",
            "timeout_sec",
        ],
    )
    if missing_command:
        return False, "E_BAD_REQUEST", f"Missing command.{missing_command}"

    op = str(command.get("op", ""))
    if not is_known_action(op, allow_alias=False):
        return False, "E_UNKNOWN_ACTION", f"unknown op: {op}"

    if not isinstance(command.get("ros"), dict):
        return False, "E_BAD_REQUEST", "command.ros must be an object"

    if not isinstance(command.get("params"), dict):
        return False, "E_BAD_REQUEST", "command.params must be an object"

    return True, "R_ACCEPTED", "OK"


def validate_agent_result_v5(result: JSONDict) -> Tuple[bool, str, str]:
    ok, code, msg = validate_common_fields_v5(result, expected_mt="agent_result")
    if not ok:
        return ok, code, msg

    missing = required_fields(result, ["ref", "robot_id", "command", "ok", "code", "message", "state", "perf", "err"])
    if missing:
        return False, "E_BAD_REQUEST", f"Missing agent_result.{missing}"

    command = result.get("command")
    if not isinstance(command, dict):
        return False, "E_BAD_REQUEST", "agent_result.command must be an object"

    missing_command = required_fields(command, ["command_id", "op"])
    if missing_command:
        return False, "E_BAD_REQUEST", f"Missing command.{missing_command}"

    if not isinstance(result.get("state"), dict):
        return False, "E_BAD_REQUEST", "agent_result.state must be an object"

    if not isinstance(result.get("perf"), dict):
        return False, "E_BAD_REQUEST", "agent_result.perf must be an object"

    if not isinstance(result.get("err"), list):
        return False, "E_BAD_REQUEST", "agent_result.err must be an array"

    code_value = result.get("code")
    if code_value not in RESULT_CODES_OK and code_value not in RESULT_CODES_ERROR:
        return False, "E_BAD_REQUEST", f"unknown result code: {code_value}"

    return True, "R_ACCEPTED", "OK"


def validate_client_heartbeat_response_v5(message: JSONDict) -> Tuple[bool, str, str]:
    ok, code, msg = validate_common_fields_v5(message, expected_mt="client_heartbeat_response")
    if not ok:
        return ok, code, msg
    missing = required_fields(message, ["ref", "ok", "code", "message", "client"])
    if missing:
        return False, "E_BAD_REQUEST", f"Missing client_heartbeat_response.{missing}"
    if not isinstance(message.get("client"), dict):
        return False, "E_BAD_REQUEST", "client_heartbeat_response.client must be an object"
    robots = message.get("robots", {})
    if robots is not None and not isinstance(robots, dict):
        return False, "E_BAD_REQUEST", "client_heartbeat_response.robots must be an object if present"
    code_value = message.get("code")
    if code_value not in RESULT_CODES_OK and code_value not in RESULT_CODES_ERROR:
        return False, "E_BAD_REQUEST", f"unknown result code: {code_value}"
    return True, "R_ACCEPTED", "OK"


def validate_server_command_v4(cmd: JSONDict) -> Tuple[bool, str, str]:
    ok, code, msg = validate_common_fields(cmd, expected_mt="server_command")
    if not ok:
        return ok, code, msg

    command = cmd.get("command")
    if not isinstance(command, dict):
        return False, "E_BAD_REQUEST", "server_command.command must be an object"

    missing_command = required_fields(
        command,
        [
            "command_id",
            "command_revision",
            "op",
            "server_priority",
            "blocking_type",
            "interrupt_policy",
            "robot_id",
            "ros",
            "params",
            "timeout_sec",
        ],
    )
    if missing_command:
        return False, "E_BAD_REQUEST", f"Missing command.{missing_command}"

    op = str(command.get("op", ""))
    if not is_known_action(op, allow_alias=False):
        return False, "E_UNKNOWN_ACTION", f"unknown op: {op}"

    if not isinstance(command.get("ros"), dict):
        return False, "E_BAD_REQUEST", "command.ros must be an object"

    if not isinstance(command.get("params"), dict):
        return False, "E_BAD_REQUEST", "command.params must be an object"

    return True, "R_ACCEPTED", "OK"


def validate_agent_result_v4(result: JSONDict) -> Tuple[bool, str, str]:
    ok, code, msg = validate_common_fields(result, expected_mt="agent_result")
    if not ok:
        return ok, code, msg

    missing = required_fields(result, ["ref", "robot_id", "command", "ok", "code", "message", "state", "perf", "err"])
    if missing:
        return False, "E_BAD_REQUEST", f"Missing agent_result.{missing}"

    command = result.get("command")
    if not isinstance(command, dict):
        return False, "E_BAD_REQUEST", "agent_result.command must be an object"

    missing_command = required_fields(command, ["command_id", "op"])
    if missing_command:
        return False, "E_BAD_REQUEST", f"Missing command.{missing_command}"

    state = result.get("state")
    if not isinstance(state, dict):
        return False, "E_BAD_REQUEST", "agent_result.state must be an object"

    code_value = result.get("code")
    if code_value not in RESULT_CODES_OK and code_value not in RESULT_CODES_ERROR:
        return False, "E_BAD_REQUEST", f"unknown result code: {code_value}"

    return True, "R_ACCEPTED", "OK"


def validate_heartbeat_response_v4(message: JSONDict) -> Tuple[bool, str, str]:
    ok, code, msg = validate_common_fields(message, expected_mt="heartbeat_response")
    if not ok:
        return ok, code, msg
    missing = required_fields(message, ["ref", "robot_id", "ok", "agent_alive"])
    if missing:
        return False, "E_BAD_REQUEST", f"Missing heartbeat_response.{missing}"
    return True, "R_ACCEPTED", "OK"


def validate_heartbeat_request_v4(message: JSONDict) -> Tuple[bool, str, str]:
    ok, code, msg = validate_common_fields(message, expected_mt="heartbeat_request")
    if not ok:
        return ok, code, msg
    missing = required_fields(message, ["robot_id"])
    if missing:
        return False, "E_BAD_REQUEST", f"Missing heartbeat_request.{missing}"
    return True, "R_ACCEPTED", "OK"


def validate_state_report_v4(message: JSONDict) -> Tuple[bool, str, str]:
    ok, code, msg = validate_common_fields(message, expected_mt="state_report")
    if not ok:
        return ok, code, msg
    missing = required_fields(message, ["robot_id", "state"])
    if missing:
        return False, "E_BAD_REQUEST", f"Missing state_report.{missing}"
    if not isinstance(message.get("state"), dict):
        return False, "E_BAD_REQUEST", "state_report.state must be an object"
    return True, "R_ACCEPTED", "OK"


def validate_action_policy_entry(action: str, policy: JSONDict) -> Tuple[bool, str, str]:
    if action in ACTION_ALIASES:
        canonical_action = ACTION_ALIASES[action]
        return False, "E_BAD_REQUEST", f"policy action must be canonical: {action} -> {canonical_action}"

    if not is_known_action(action, allow_alias=False):
        return False, "E_UNKNOWN_ACTION", f"unknown policy action: {action}"

    if not isinstance(policy, dict):
        return False, "E_BAD_REQUEST", f"policy for {action} must be an object"

    missing = required_fields(
        policy,
        [
            "priority",
            "command_type",
            "blocking_type",
            "interrupt_policy",
            "allowed_operating_modes",
            "target_scope_allowed",
        ],
    )
    if missing:
        return False, "E_BAD_REQUEST", f"policy.{action} missing {missing}"

    try:
        priority = int(policy.get("priority"))
    except Exception:
        return False, "E_BAD_REQUEST", f"policy.{action}.priority must be an integer"
    if priority <= 0:
        return False, "E_BAD_REQUEST", f"policy.{action}.priority must be positive"

    if policy.get("command_type") not in COMMAND_TYPES:
        return False, "E_BAD_REQUEST", f"policy.{action}.command_type is invalid"

    if policy.get("blocking_type") not in BLOCKING_TYPES:
        return False, "E_BAD_REQUEST", f"policy.{action}.blocking_type is invalid"

    if policy.get("interrupt_policy") not in INTERRUPT_POLICIES:
        return False, "E_BAD_REQUEST", f"policy.{action}.interrupt_policy is invalid"

    allowed_modes = policy.get("allowed_operating_modes")
    if not isinstance(allowed_modes, list) or not allowed_modes:
        return False, "E_BAD_REQUEST", f"policy.{action}.allowed_operating_modes must be a non-empty array"
    if "READY" in allowed_modes:
        return False, "E_BAD_REQUEST", f"policy.{action} must not use READY as an operating_mode"
    for mode in allowed_modes:
        if mode != "ANY" and mode not in OPERATING_MODES:
            return False, "E_BAD_REQUEST", f"policy.{action}.allowed_operating_modes has invalid mode: {mode}"

    target_scopes = policy.get("target_scope_allowed")
    if not isinstance(target_scopes, list) or not target_scopes:
        return False, "E_BAD_REQUEST", f"policy.{action}.target_scope_allowed must be a non-empty array"
    for scope in target_scopes:
        if scope not in TARGET_SCOPES:
            return False, "E_BAD_REQUEST", f"policy.{action}.target_scope_allowed has invalid scope: {scope}"

    return True, "R_ACCEPTED", "OK"


def validate_action_policy_table(table: JSONDict) -> Tuple[bool, str, str]:
    if not isinstance(table, dict):
        return False, "E_BAD_REQUEST", "action policy table must be an object"

    policies = table.get("actions", table)
    if not isinstance(policies, dict):
        return False, "E_BAD_REQUEST", "action policy actions must be an object"

    for required_action in ["all_stop", "robot_stop", "status_request", "move_forward"]:
        if required_action not in policies:
            return False, "E_BAD_REQUEST", f"missing required action policy: {required_action}"

    for action, policy in policies.items():
        ok, code, msg = validate_action_policy_entry(str(action), policy)
        if not ok:
            return ok, code, msg

    return True, "R_ACCEPTED", "OK"


def get_action_policy(table: JSONDict, action: str) -> Optional[JSONDict]:
    policies = table.get("actions", table)
    if not isinstance(policies, dict):
        return None
    normalized_action = normalize_action(action)
    policy = policies.get(normalized_action)
    if isinstance(policy, dict):
        return policy
    return None


def validate_operator_request(req: JSONDict) -> Tuple[bool, str, str]:
    missing = required_fields(req, ["v", "mt", "id", "ts", "user", "target", "action", "params"])
    if missing:
        return False, "E_SERVER_BAD_OPERATOR_REQUEST", f"Missing operator_request.{missing}"
    if req.get("mt") != "operator_request":
        return False, "E_SERVER_BAD_OPERATOR_REQUEST", "mt must be operator_request"
    if req.get("v") != 1:
        return False, "E_SERVER_BAD_OPERATOR_REQUEST", "operator_request.v must be 1"
    if not isinstance(req.get("params"), dict):
        return False, "E_SERVER_BAD_OPERATOR_REQUEST", "operator_request.params must be an object"
    return True, "R_OK", "OK"


def validate_json_command_v03(cmd: JSONDict) -> Tuple[bool, str, str]:
    missing = required_fields(cmd, ["v", "mt", "id", "ts", "job", "to", "op", "ros", "topic", "p", "lim"])
    if missing:
        return False, "E_MISSING_FIELD", f"Missing json_command.{missing}"
    if cmd.get("v") != 3:
        return False, "E_INVALID_VERSION", "json_command.v must be 3"
    if cmd.get("mt") != "cmd":
        return False, "E_INVALID_MESSAGE_TYPE", "json_command.mt must be cmd"
    if not isinstance(cmd.get("p"), dict):
        return False, "E_INVALID_PARAM", "json_command.p must be an object"
    if not isinstance(cmd.get("lim"), dict):
        return False, "E_INVALID_PARAM", "json_command.lim must be an object"
    return True, "R_OK", "OK"


def validate_json_result_v03(res: JSONDict) -> Tuple[bool, str, str]:
    missing = required_fields(res, ["v", "mt", "id", "ref", "ts", "job", "from", "op", "ok", "st", "code", "perf", "err"])
    if missing:
        return False, "E_SERVER_BAD_RESULT_JSON", f"Missing json_result.{missing}"
    if res.get("v") != 3:
        return False, "E_SERVER_BAD_RESULT_JSON", "json_result.v must be 3"
    if res.get("mt") != "res":
        return False, "E_SERVER_BAD_RESULT_JSON", "json_result.mt must be res"
    if not isinstance(res.get("err"), list):
        return False, "E_SERVER_BAD_RESULT_JSON", "json_result.err must be an array"
    return True, "R_OK", "OK"


def validate_result_matches_command(cmd: JSONDict, res: JSONDict) -> Tuple[bool, str]:
    checks = [
        (cmd.get("id"), res.get("ref"), "command.id != result.ref"),
        (cmd.get("job"), res.get("job"), "command.job != result.job"),
        (cmd.get("to"), res.get("from"), "command.to != result.from"),
        (cmd.get("op"), res.get("op"), "command.op != result.op"),
    ]
    for expected, actual, message in checks:
        if expected != actual:
            return False, message
    return True, "OK"


def make_synthetic_result(
    command: JSONDict,
    result_id: str,
    code: str,
    msg: str,
    where: str = "fleet_server",
    st: str = "failed",
    detail: Optional[JSONDict] = None,
) -> JSONDict:
    return {
        "v": 3,
        "mt": "res",
        "id": result_id,
        "ref": command.get("id", ""),
        "ts": now_ts(),
        "job": command.get("job", ""),
        "from": command.get("to", ""),
        "op": command.get("op", ""),
        "ok": False,
        "st": st,
        "code": code,
        "perf": {
            "dur": 0.0,
            "pub": 0,
        },
        "err": [
            error_entry(code, msg, where, detail),
        ],
    }


def get_local_ip_candidates() -> list[str]:
    ips = set()
    try:
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None):
            ip = info[4][0]
            if "." in ip and not ip.startswith("127."):
                ips.add(ip)
    except Exception:
        pass

    try:
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_sock.settimeout(1.0)
        test_sock.connect(("8.8.8.8", 80))
        ip = test_sock.getsockname()[0]
        if ip and not ip.startswith("127."):
            ips.add(ip)
        test_sock.close()
    except Exception:
        pass

    return sorted(ips)
