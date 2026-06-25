import argparse
import json
import shlex
import shutil
import subprocess
import socket
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fleet_protocol import (
    FLEET_JSON_SCHEMA,
    FLEET_JSON_VERSION,
    FLEET_JSON_VERSION_V5,
    FLEET_JSON_SCHEMA_V5,
    FLEET_JSON_VERSION_V6,
    FLEET_JSON_SCHEMA_V6,
    IdGenerator,
    ProtocolError,
    error_entry,
    get_action_policy,
    get_local_ip_candidates,
    make_common_message,
    make_job_id,
    make_msg_id,
    make_synthetic_result,
    now_ts,
    normalize_action,
    pretty_json,
    recv_json_line,
    save_json_file,
    save_json_log,
    send_json,
    validate_action_policy_table,
    validate_agent_result_v4,
    validate_agent_result_v5,
    validate_auth,
    validate_control_command_request_v5,
    validate_control_data_request_v5,
    validate_control_health_request_v5,
    validate_client_heartbeat_response_v5,
    validate_heartbeat_request_v4,
    validate_heartbeat_response_v4,
    validate_json_command_v03,
    validate_json_result_v03,
    validate_operator_request,
    validate_operator_request_v4,
    validate_operator_request_v5,
    validate_result_matches_command,
    validate_server_command_v4,
    validate_server_command_v5,
    validate_state_report_v4,
)


SCRIPT_DIR = Path(__file__).resolve().parent


MOVE_ACTIONS = {"move_forward", "move_backward", "turn_left", "turn_right", "custom_move"}
STOP_ACTIONS = {"stop", "robot_stop", "all_stop", "emergency_stop"}
SYSTEM_ACTIONS = {
    "status_request",
    "robot_state_request",
    "job_status_request",
    "ping",
    "mapping_status",
    "map_status",
    "map_list",
    "nav_status",
}
FILE_TRANSFER_ACTIONS = {"image_request", "image_view_closed", "file_cleanup_report", "map_image_select"}
SUPPORTED_ACTIONS = MOVE_ACTIONS | STOP_ACTIONS | SYSTEM_ACTIONS | FILE_TRANSFER_ACTIONS
# Accepted inbound schemas during v5→v6 transition
FLEET_JSON_SCHEMA_V5_COMPAT = {
    "fleet_json_v0.5",
    FLEET_JSON_SCHEMA_V5,
    FLEET_JSON_SCHEMA_V6,
}
CONTROL_REQUEST_TYPES_V5 = {
    "control_health_request",
    "control_command_request",
    "control_data_request",
    "operator_request",
}
CONTROL_CHANNEL_MESSAGE_TYPES_V5 = {
    "health": {"control_health_request"},
    "command": {"operator_request", "control_command_request"},
    "data_control": {"control_data_request"},
}


def resolve_path(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return SCRIPT_DIR / path


def load_required_json(path: Path, label: str) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Missing required {label}: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON in {label}: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"{label} root must be a JSON object: {path}")
    return data


def as_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def as_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return int(default)


def safe_file_name(value: Any, fallback: str = "file") -> str:
    text = str(value or "").strip().replace("\\", "_").replace("/", "_")
    safe = "".join(ch if ch.isalnum() or ch in {".", "_", "-"} else "_" for ch in text)
    safe = safe.strip("._")
    return safe or fallback


class FleetServer:
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        self.config = load_required_json(config_path, "server_config")
        self._validate_required_object(self.config, "server_config", ["server", "files", "logs", "defaults", "limits", "safety"])

        files = self._required_object(self.config, "files", "server_config.files")
        client_info_file = self._required_text(files, "client_info_file", "server_config.files.client_info_file")
        self.client_info_path = resolve_path(str(client_info_file))
        self.client_info = load_required_json(self.client_info_path, "client_info")
        self._validate_required_object(self.client_info, "client_info", ["robot_command_client", "robots"])
        self.registry_path = self.client_info_path
        self.registry = {
            "robots": self.client_info.get("robots", {}),
        }

        control_info_file = self._required_text(files, "control_info_file", "server_config.files.control_info_file")
        self.control_info_path = resolve_path(str(control_info_file))
        self.control_info = load_required_json(self.control_info_path, "control_info")
        self._validate_required_object(self.control_info, "control_info", ["control_ui", "image_transfer"])

        action_policy_file = self._required_text(files, "action_policy_file", "server_config.files.action_policy_file")
        self.action_policy_path = resolve_path(str(action_policy_file))
        self.action_policy = load_required_json(self.action_policy_path, "action_policy")
        policy_ok, policy_code, policy_msg = validate_action_policy_table(self.action_policy)
        if not policy_ok:
            raise RuntimeError(f"Invalid action policy table ({policy_code}): {policy_msg}")

        logs = self._required_object(self.config, "logs", "server_config.logs")
        self.log_base = resolve_path(self._required_text(logs, "base_dir", "server_config.logs.base_dir"))
        self.ids = IdGenerator()
        self.state_lock = threading.Lock()
        self.robot_states: Dict[str, Dict[str, Any]] = {}
        self.global_state = "NORMAL"
        self.seen_command_ids: set[str] = set()
        self.started_monotonic = time.monotonic()
        self._suppress_operator_response_log = False
        self._last_client_connection_state: Optional[str] = None

        self._validate_runtime_config()

    def _validate_required_object(self, data: Dict[str, Any], label: str, keys: List[str]) -> None:
        for key in keys:
            if key not in data:
                raise RuntimeError(f"{label}.{key} is required")
            if not isinstance(data[key], dict):
                raise RuntimeError(f"{label}.{key} must be a JSON object")

    def _required_object(self, data: Dict[str, Any], key: str, label: str) -> Dict[str, Any]:
        value = data.get(key)
        if not isinstance(value, dict):
            raise RuntimeError(f"{label} must be a JSON object")
        return value

    def _required_text(self, data: Dict[str, Any], key: str, label: str) -> str:
        value = data.get(key)
        text = str(value).strip() if value is not None else ""
        if not text:
            raise RuntimeError(f"{label} is required")
        return text

    def _required_int(self, data: Dict[str, Any], key: str, label: str) -> int:
        if key not in data:
            raise RuntimeError(f"{label} is required")
        try:
            value = int(data[key])
        except Exception as exc:
            raise RuntimeError(f"{label} must be an integer") from exc
        if not (1 <= value <= 65535):
            raise RuntimeError(f"{label} must be a TCP port between 1 and 65535")
        return value

    def _validate_runtime_config(self) -> None:
        server = self._required_object(self.config, "server", "server_config.server")
        self._required_text(server, "bind_ip", "server_config.server.bind_ip")
        self._required_int(server, "control_port", "server_config.server.control_port")
        for key in ("control_health_port", "control_command_port", "control_data_port"):
            self._required_int(server, key, f"server_config.server.{key}")
        if "socket_timeout" not in server:
            raise RuntimeError("server_config.server.socket_timeout is required")

        client = self._robot_command_client()
        for key in ("id", "ip", "health_port", "command_port", "data_control_port"):
            if key.endswith("_port"):
                self._required_int(client, key, f"client_info.robot_command_client.{key}")
            else:
                self._required_text(client, key, f"client_info.robot_command_client.{key}")

        robots = self._required_object(self.client_info, "robots", "client_info.robots")
        if not robots:
            raise RuntimeError("client_info.robots must contain at least one robot")
        for robot_key, robot_info in robots.items():
            if not isinstance(robot_info, dict):
                raise RuntimeError(f"client_info.robots.{robot_key} must be a JSON object")
            for key in ("robot_id", "namespace", "topic", "ros_domain_id"):
                if key == "ros_domain_id":
                    if key not in robot_info:
                        raise RuntimeError(f"client_info.robots.{robot_key}.{key} is required")
                    int(robot_info[key])
                else:
                    self._required_text(robot_info, key, f"client_info.robots.{robot_key}.{key}")

        control = self._required_object(self.control_info, "control_ui", "control_info.control_ui")
        self._required_text(control, "ip", "control_info.control_ui.ip")
        self._required_text(control, "user", "control_info.control_ui.user")
        control_json = self._required_object(control, "json", "control_info.control_ui.json")
        control_ports = self._control_ports()
        control_port_sections = {
            "health": control_ports["health_port"],
            "command": control_ports["command_port"],
            "data_control": control_ports["data_control_port"],
        }
        for section_name, expected_port in control_port_sections.items():
            section = self._required_object(control_json, section_name, f"control_info.control_ui.json.{section_name}")
            self._required_text(section, "server_ip", f"control_info.control_ui.json.{section_name}.server_ip")
            port = self._required_int(section, "server_port", f"control_info.control_ui.json.{section_name}.server_port")
            if port != expected_port:
                raise RuntimeError(
                    f"control_info.control_ui.json.{section_name}.server_port ({port}) "
                    f"must match server_config.server control port ({expected_port})"
                )
        ssh = self._required_object(control, "ssh", "control_info.control_ui.ssh")
        self._required_int(ssh, "port", "control_info.control_ui.ssh.port")
        if "connect_timeout" not in ssh:
            raise RuntimeError("control_info.control_ui.ssh.connect_timeout is required")
        paths = self._required_object(control, "paths", "control_info.control_ui.paths")
        self._required_text(paths, "image_cache_dir", "control_info.control_ui.paths.image_cache_dir")

        image_transfer = self._required_object(self.control_info, "image_transfer", "control_info.image_transfer")
        for key in ("method", "direction", "default_server_path"):
            self._required_text(image_transfer, key, f"control_info.image_transfer.{key}")

        transfer_config = self._required_object(self.config, "file_transfer", "server_config.file_transfer")
        self._required_text(transfer_config, "rsync_bin", "server_config.file_transfer.rsync_bin")
        self._required_text(transfer_config, "server_image_dir", "server_config.file_transfer.server_image_dir")
        raw_dirs = transfer_config.get("allowed_source_dirs")
        if not isinstance(raw_dirs, list) or not raw_dirs:
            raise RuntimeError("server_config.file_transfer.allowed_source_dirs must be a non-empty list")

    def _robot_command_client(self) -> Dict[str, Any]:
        client = self.client_info.get("robot_command_client", {})
        if isinstance(client, dict):
            return client
        raise RuntimeError("client_info.robot_command_client must be a JSON object")

    def _robot_command_client_id(self) -> str:
        return self._required_text(self._robot_command_client(), "id", "client_info.robot_command_client.id")

    def _robot_command_address(self, channel: str = "command") -> Tuple[str, int]:
        client = self._robot_command_client()
        ip = self._required_text(client, "ip", "client_info.robot_command_client.ip")
        port_keys = {
            "health": "health_port",
            "command": "command_port",
            "data_control": "data_control_port",
        }
        if channel not in port_keys:
            raise RuntimeError(f"unknown robot command channel: {channel}")
        port_key = port_keys[channel]
        port = self._required_int(client, port_key, f"client_info.robot_command_client.{port_key}")
        return ip, port

    def _robot_command_ports(self) -> Dict[str, int]:
        client = self._robot_command_client()
        return {
            "health_port": self._required_int(client, "health_port", "client_info.robot_command_client.health_port"),
            "command_port": self._required_int(client, "command_port", "client_info.robot_command_client.command_port"),
            "data_control_port": self._required_int(client, "data_control_port", "client_info.robot_command_client.data_control_port"),
        }

    def _control_ports(self) -> Dict[str, int]:
        server = self._required_object(self.config, "server", "server_config.server")
        return {
            "health_port": self._required_int(server, "control_health_port", "server_config.server.control_health_port"),
            "command_port": self._required_int(server, "control_command_port", "server_config.server.control_command_port"),
            "data_control_port": self._required_int(server, "control_data_port", "server_config.server.control_data_port"),
            "client_event_port": self._required_int(server, "client_event_port", "server_config.server.client_event_port"),
        }

    def _robot_alias_values(self, robot_key: str, info: Dict[str, Any]) -> set[str]:
        values = {str(robot_key)}
        for field in ("robot_id", "alias", "display_name"):
            value = info.get(field)
            if value is not None:
                values.add(str(value))
        aliases = info.get("aliases", [])
        if isinstance(aliases, list):
            values.update(str(alias) for alias in aliases if str(alias).strip())
        return {value.strip() for value in values if value.strip()}

    def _canonical_robot_key(self, target: str) -> Optional[str]:
        target_text = str(target).strip()
        robots = self.registry.get("robots", {})
        if target_text in robots:
            return target_text
        for robot_key, info in robots.items():
            if not isinstance(info, dict):
                continue
            if target_text in self._robot_alias_values(str(robot_key), info):
                return str(robot_key)
        return None

    def _wire_robot_id(self, robot_key: str) -> str:
        info = self.registry.get("robots", {}).get(robot_key, {})
        if isinstance(info, dict):
            return self._required_text(info, "robot_id", f"client_info.robots.{robot_key}.robot_id")
        raise RuntimeError(f"client_info.robots.{robot_key} must be a JSON object")

    def _control_ui_info(self) -> Dict[str, Any]:
        control = self.control_info.get("control_ui", {})
        if isinstance(control, dict):
            return control
        raise RuntimeError("control_info.control_ui must be a JSON object")

    def _control_image_transfer_defaults(self) -> Dict[str, str]:
        control = self._control_ui_info()
        ssh = self._required_object(control, "ssh", "control_info.control_ui.ssh")
        paths = self._required_object(control, "paths", "control_info.control_ui.paths")
        image_transfer = self._required_object(self.control_info, "image_transfer", "control_info.image_transfer")
        return {
            "method": self._required_text(image_transfer, "method", "control_info.image_transfer.method"),
            "direction": self._required_text(image_transfer, "direction", "control_info.image_transfer.direction"),
            "control_host": self._required_text(control, "ip", "control_info.control_ui.ip"),
            "control_user": self._required_text(control, "user", "control_info.control_ui.user"),
            "control_dir": self._required_text(paths, "image_cache_dir", "control_info.control_ui.paths.image_cache_dir"),
            "ssh_port": str(self._required_int(ssh, "port", "control_info.control_ui.ssh.port")),
            "ssh_connect_timeout": self._required_text(ssh, "connect_timeout", "control_info.control_ui.ssh.connect_timeout"),
            "identity_file": str(ssh.get("identity_file", "")).strip(),
            "default_server_path": self._required_text(image_transfer, "default_server_path", "control_info.image_transfer.default_server_path"),
        }

    def _save_log(self, category: str, prefix: str, data: Dict[str, Any]) -> Tuple[Path, Path]:
        if self._suppress_operator_response_log and category == "operator_responses" and prefix == "operator_response":
            folder = self.log_base / category
            return folder / f"{prefix}_suppressed.json", folder / f"latest_{prefix}.json"
        history_path, latest_path = save_json_log(self.log_base, category, prefix, data)
        if bool(self.config["logs"].get("print_paths", True)):
            print(f"[LOG] {category}/{prefix} latest={latest_path}")
        return history_path, latest_path

    def _print_request_summary(self, req: Dict[str, Any], peer_ip: str) -> None:
        if req.get("v") in {FLEET_JSON_VERSION, FLEET_JSON_VERSION_V5, FLEET_JSON_VERSION_V6}:
            command = req.get("command", {})
            if not isinstance(command, dict):
                command = {}
            request = req.get("request", {})
            if not isinstance(request, dict):
                request = {}
            print(
                "[OPERATOR REQUEST] "
                f"peer={peer_ip} "
                f"msg_id={req.get('msg_id', '')} "
                f"command_id={command.get('command_id', '')} "
                f"mt={req.get('mt', '')} "
                f"targets={command.get('targets', request.get('target', []))} "
                f"action={command.get('action', request.get('action', ''))}"
            )
            return

        print(
            "[OPERATOR REQUEST] "
            f"peer={peer_ip} "
            f"id={req.get('id', '')} "
            f"target={req.get('target', '')} "
            f"action={req.get('action', '')}"
        )

    def _print_response_summary(self, response: Dict[str, Any]) -> None:
        result_codes = {}
        for robot_id, result in response.get("results", {}).items():
            if isinstance(result, dict):
                result_codes[robot_id] = result.get("code", "")
        if response.get("v") in {FLEET_JSON_VERSION, FLEET_JSON_VERSION_V5, FLEET_JSON_VERSION_V6}:
            command = response.get("command", {})
            if not isinstance(command, dict):
                command = {}
            print(
                "[OPERATOR RESPONSE] "
                f"ref={response.get('ref', '')} "
                f"ok={response.get('ok')} "
                f"code={response.get('code', '')} "
                f"command_id={command.get('command_id', '')} "
                f"results={result_codes}"
            )
            return
        print(
            "[OPERATOR RESPONSE] "
            f"ref={response.get('ref', '')} "
            f"ok={response.get('ok')} "
            f"code={response.get('code', '')} "
            f"job={response.get('job', '')} "
            f"results={result_codes}"
        )

    def run(self) -> None:
        server_config = self._required_object(self.config, "server", "server_config.server")
        bind_ip = self._required_text(server_config, "bind_ip", "server_config.server.bind_ip")
        control_ports = self._control_ports()
        listeners = [
            ("health", control_ports["health_port"]),
            ("command", control_ports["command_port"]),
            ("data_control", control_ports["data_control_port"]),
            ("client_event", control_ports["client_event_port"]),
        ]
        timeout = float(server_config["socket_timeout"])

        self._log_startup()
        print("========================================")
        print("TurtleBot Fleet Server")
        print("role: Operator HMI <-> Fleet Server <-> Robot Agents")
        print("protocol: TCP UTF-8 NDJSON, one JSON object per line")
        print("========================================")
        print(f"config: {self.config_path}")
        print(f"client_info: {self.client_info_path}")
        print(f"control_info: {self.control_info_path}")
        print(f"action_policy: {self.action_policy_path}")
        print(f"logs: {self.log_base}")
        print(f"local IP candidates: {', '.join(get_local_ip_candidates()) or 'none'}")
        print(
            "listening: "
            + ", ".join(f"{channel}={bind_ip}:{port}" for channel, port in listeners)
        )
        print("Ctrl+C to stop")
        print()

        server_socks: List[Tuple[str, int, socket.socket]] = []
        try:
            for channel, port in listeners:
                server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_sock.bind((bind_ip, port))
                server_sock.listen(20)
                server_sock.settimeout(0.2)
                server_socks.append((channel, port, server_sock))
        except OSError:
            for _channel, _port, server_sock in server_socks:
                server_sock.close()
            raise

        _shutdown_reason = "unexpected"
        try:
            while True:
                for channel, listener_port, server_sock in server_socks:
                    try:
                        conn, addr = server_sock.accept()
                    except socket.timeout:
                        continue
                    conn.settimeout(timeout)
                    if channel == "client_event":
                        thread = threading.Thread(
                            target=self._handle_client_event_connection,
                            args=(conn, addr),
                            daemon=True,
                        )
                    else:
                        thread = threading.Thread(
                            target=self._handle_control_connection,
                            args=(conn, addr, channel, listener_port),
                            daemon=True,
                        )
                    thread.start()
        except KeyboardInterrupt:
            print("\n[STOP] Fleet server stopped by user")
            _shutdown_reason = "user_interrupt"
        finally:
            self._log_shutdown(_shutdown_reason)
            for _channel, _port, server_sock in server_socks:
                server_sock.close()

    def _handle_control_connection(
        self,
        conn: socket.socket,
        addr: Tuple[str, int],
        control_channel: str = "unknown",
        listener_port: int = 0,
    ) -> None:
        peer_ip, peer_port = addr
        print(f"[CONTROL CONNECT] channel={control_channel} listen_port={listener_port} peer={peer_ip}:{peer_port}")

        allowed_ips = self.config["server"].get("allowed_control_ips", [])
        if allowed_ips and peer_ip not in allowed_ips:
            response = self._operator_error_response(
                req=None,
                code="E_SERVER_CONTROL_IP_BLOCKED",
                msg=f"Control client IP {peer_ip} is not allowed",
                detail={"peer_ip": peer_ip, "allowed_control_ips": allowed_ips},
            )
            try:
                send_json(conn, response)
            finally:
                conn.close()
            return

        try:
            with conn:
                file_obj = conn.makefile("r", encoding="utf-8")
                while True:
                    try:
                        req = recv_json_line(file_obj)
                    except ProtocolError as exc:
                        response = self._operator_error_response(
                            req=None,
                            code="E_BAD_JSON",
                            msg=str(exc),
                        )
                        send_json(conn, response)
                        continue

                    if req is None:
                        break

                    response = self.handle_operator_request(req, peer_ip, control_channel=control_channel)
                    send_json(conn, response)
        except OSError as exc:
            print(f"[CONTROL ERROR] channel={control_channel} listen_port={listener_port} peer={peer_ip}:{peer_port} {exc}")
        finally:
            print(f"[CONTROL CLOSE] channel={control_channel} listen_port={listener_port} peer={peer_ip}:{peer_port}")

    def _handle_client_event_connection(
        self,
        conn: socket.socket,
        addr: Tuple[str, int],
    ) -> None:
        peer_ip, peer_port = addr
        print(f"[CLIENT EVENT CONNECT] peer={peer_ip}:{peer_port}")
        ack: Dict[str, Any] = {
            "v": FLEET_JSON_VERSION_V6,
            "mt": "mapping_complete_ack",
            "ts": now_ts(),
            "source": "fleet_server",
            "dest": "robot_command_client",
            "schema": FLEET_JSON_SCHEMA_V6,
        }
        try:
            with conn:
                file_obj = conn.makefile("r", encoding="utf-8")
                req = recv_json_line(file_obj)
                if req is None or not isinstance(req, dict):
                    ack.update({"ok": False, "code": "E_BAD_JSON", "message": "empty or invalid JSON"})
                    send_json(conn, ack)
                    return

                mt = str(req.get("mt", ""))
                if mt != "mapping_complete_notification":
                    ack.update({
                        "ok": False,
                        "code": "E_BAD_REQUEST",
                        "message": f"expected mt=mapping_complete_notification, got {mt}",
                    })
                    send_json(conn, ack)
                    return

                notification = req.get("notification", {})
                if not isinstance(notification, dict):
                    ack.update({"ok": False, "code": "E_BAD_REQUEST", "message": "notification must be a JSON object"})
                    send_json(conn, ack)
                    return

                map_dir_name = str(notification.get("map_dir_name") or "").strip()
                client_map_dir = str(notification.get("client_map_dir") or "").strip()
                robot_alias = str(notification.get("robot_alias") or notification.get("robot_id") or "").strip()

                if not map_dir_name or not client_map_dir:
                    ack.update({
                        "ok": False,
                        "code": "E_BAD_REQUEST",
                        "message": "notification must include map_dir_name and client_map_dir",
                    })
                    send_json(conn, ack)
                    return

                ack.update({
                    "ref": req.get("msg_id", ""),
                    "ok": True,
                    "code": "R_ACCEPTED",
                    "message": f"mapping complete notification received for {map_dir_name}, sync will begin",
                })
                send_json(conn, ack)
                self._save_log("client_data", "mapping_complete_notification", req)
                print(f"[CLIENT EVENT] mapping_complete_notification: robot={robot_alias} dir={map_dir_name}")
        except OSError as exc:
            print(f"[CLIENT EVENT ERROR] peer={peer_ip}:{peer_port} {exc}")
            return

        sync_thread = threading.Thread(
            target=self._auto_sync_map_from_client_v5,
            args=(robot_alias, map_dir_name, client_map_dir),
            daemon=True,
        )
        sync_thread.start()

    def handle_operator_request(self, req: Dict[str, Any], peer_ip: str, control_channel: str = "command") -> Dict[str, Any]:
        self._save_log("operator_requests", "operator_request", req)
        self._print_request_summary(req, peer_ip)

        if self._is_control_request_v5(req):
            return self.handle_control_request_v5(req, peer_ip, control_channel=control_channel)

        if control_channel not in {"command", "unknown"}:
            return self._operator_error_response(
                req,
                "E_BAD_REQUEST",
                f"legacy operator_request is only accepted on command port; received on {control_channel}",
                {"control_channel": control_channel},
            )

        if req.get("v") == FLEET_JSON_VERSION:
            return self.handle_operator_request_v4(req, peer_ip)

        ok, code, msg = validate_operator_request(req)
        if not ok:
            return self._operator_error_response(req, code, msg)

        target = str(req.get("target", "")).strip()
        action = str(req.get("action", "")).strip()
        params = req.get("params", {})

        if action not in SUPPORTED_ACTIONS:
            return self._operator_error_response(
                req,
                "E_SERVER_UNSUPPORTED_ACTION",
                f"Unsupported action: {action}",
                {"supported_actions": sorted(SUPPORTED_ACTIONS)},
            )

        if action == "ping":
            return self._operator_ok_response(req, "R_PONG", "pong", status=self._server_status())

        if action == "status_request":
            return self._operator_ok_response(req, "R_STATUS", "status", status=self._server_status())

        targets, target_err = self._resolve_targets(target, action)
        if target_err is not None:
            return self._operator_error_response(req, target_err[0], target_err[1])

        safety_ok, safety_code, safety_msg = self._check_server_safety(action, targets)
        if not safety_ok:
            return self._operator_error_response(req, safety_code, safety_msg)

        job_id = self.ids.next("J", "ALL_STOP" if action == "all_stop" else "")
        results: Dict[str, Any] = {}

        for robot_id in targets:
            command, build_err = self._build_json_command(req, robot_id, action, params, job_id)
            if build_err is not None:
                results[robot_id] = self._local_error_result(robot_id, action, command=None, err=build_err)
                continue
            result = self._send_command_to_agent(robot_id, command)
            results[robot_id] = result

        response = self._operator_response_from_results(req, job_id, results)
        self._save_log("operator_responses", "operator_response", response)
        self._print_response_summary(response)
        return response

    def _is_control_request_v5(self, req: Dict[str, Any]) -> bool:
        if not isinstance(req, dict):
            return False
        return req.get("v") in {FLEET_JSON_VERSION_V5, FLEET_JSON_VERSION_V6} or req.get("schema") in FLEET_JSON_SCHEMA_V5_COMPAT

    def handle_control_request_v5(self, req: Dict[str, Any], peer_ip: str, control_channel: str = "command") -> Dict[str, Any]:
        mt = str(req.get("mt", ""))
        allowed_mts = CONTROL_CHANNEL_MESSAGE_TYPES_V5.get(control_channel)
        if allowed_mts is not None and mt not in allowed_mts:
            return self._operator_error_response_v5(
                req,
                "E_BAD_REQUEST",
                f"{mt} is not accepted on {control_channel} port",
                {
                    "control_channel": control_channel,
                    "allowed_message_types": sorted(allowed_mts),
                },
            )

        ok, code, msg = self._validate_control_common_v5(req)
        if not ok:
            return self._operator_error_response_v5(req, code, msg)

        if mt == "control_health_request":
            return self._handle_control_health_request_v5(req)

        if mt in {"operator_request", "control_command_request"}:
            adapted = self._adapt_control_command_request_v5_to_v4(req)
            if adapted is None:
                return self._operator_error_response_v5(
                    req,
                    "E_BAD_REQUEST",
                    "v5 command request must include command.action/op and target/targets",
                )
            self._suppress_operator_response_log = True
            try:
                response_v4 = self.handle_operator_request_v4(adapted, peer_ip)
            finally:
                self._suppress_operator_response_log = False
            response_v5 = self._operator_response_v4_to_v5(response_v4, req)
            self._save_log("operator_responses", "operator_response", response_v5)
            self._print_response_summary(response_v5)
            return response_v5

        if mt == "control_data_request":
            adapted = self._adapt_control_data_request_v5_to_v4(req)
            if adapted is None:
                return self._operator_error_response_v5(
                    req,
                    "E_BAD_REQUEST",
                    "unsupported control_data_request; expected data_type=image or log",
                )
            self._suppress_operator_response_log = True
            try:
                response_v4 = self.handle_operator_request_v4(adapted, peer_ip)
            finally:
                self._suppress_operator_response_log = False
            response_v5 = self._operator_response_v4_to_v5(response_v4, req, mt_override="control_data_response")
            self._save_log("operator_responses", "operator_response", response_v5)
            self._print_response_summary(response_v5)
            return response_v5

        return self._operator_error_response_v5(
            req,
            "E_BAD_REQUEST",
            f"unsupported v5 message type: {mt}",
            {"supported_mt": sorted(CONTROL_REQUEST_TYPES_V5)},
        )

    def _validate_control_common_v5(self, req: Dict[str, Any]) -> Tuple[bool, str, str]:
        mt = req.get("mt") if isinstance(req, dict) else ""
        if mt == "control_health_request":
            return validate_control_health_request_v5(req)
        if mt == "operator_request":
            return validate_operator_request_v5(req)
        if mt == "control_command_request":
            return validate_control_command_request_v5(req)
        if mt == "control_data_request":
            return validate_control_data_request_v5(req)
        return False, "E_BAD_REQUEST", f"unsupported control message type: {mt}"

    def _adapt_control_command_request_v5_to_v4(self, req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        raw_command = req.get("command")
        raw_request = req.get("request")
        if not isinstance(raw_command, dict):
            if isinstance(raw_request, dict) and isinstance(raw_request.get("command"), dict):
                raw_command = raw_request.get("command")
            elif isinstance(raw_request, dict):
                raw_command = raw_request
            else:
                raw_command = {}

        action = normalize_action(
            raw_command.get("action")
            or raw_command.get("op")
            or req.get("action")
            or req.get("op")
            or ""
        )
        if not action:
            return None

        params = raw_command.get("params", {})
        if not isinstance(params, dict):
            params = {}

        targets_value = raw_command.get("targets")
        target = raw_command.get("target") or raw_command.get("robot_id") or req.get("target") or req.get("robot_id")
        if not isinstance(targets_value, list):
            if target:
                targets_value = [str(target)]
            else:
                targets_value = []

        targets = [str(item).strip() for item in targets_value if str(item).strip()]
        if not targets:
            return None

        target_scope = str(raw_command.get("target_scope") or "").strip()
        if not target_scope:
            target_scope = "all" if targets == ["all"] else "single" if len(targets) == 1 else "multi"

        command_id = str(raw_command.get("command_id") or make_msg_id("CMD", f"{action}_{'_'.join(targets)}"))
        adapted = make_common_message(
            mt="operator_request",
            source=str(req.get("source", "control_ui")),
            dest="fleet_server",
            msg_id=str(req.get("msg_id", make_msg_id("MSG", "operator_request"))),
            ts=str(req.get("ts", now_ts())),
        )
        adapted.update(
            {
                "auth": req.get("auth", {"token": self.config.get("auth", {}).get("auth_token", "team_demo_token")}),
                "user": req.get("user", "operator_1"),
                "command": {
                    "command_id": command_id,
                    "group_id": raw_command.get("group_id"),
                    "job_id": raw_command.get("job_id"),
                    "command_seq": raw_command.get("command_seq"),
                    "command_revision": int(raw_command.get("command_revision", 0)),
                    "action": action,
                    "target_scope": target_scope,
                    "targets": targets,
                    "params": params,
                    "expects": raw_command.get("expects", {"response_type": "sync", "status_followup": False}),
                    "timeout_sec": as_float(raw_command.get("timeout_sec"), as_float(self.config["defaults"].get("timeout"), 5.0)),
                },
                "ui_context": req.get("ui_context", {"client_schema": FLEET_JSON_SCHEMA_V6, "peer_mt": req.get("mt")}),
            }
        )
        return adapted

    def _adapt_control_data_request_v5_to_v4(self, req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        request = req.get("request", {})
        if not isinstance(request, dict):
            return None
        data_type = str(request.get("data_type", "")).strip()
        target = str(request.get("target") or request.get("robot_id") or "").strip()
        if not target:
            return None
        params = dict(request)
        if data_type in {"image", "map"}:
            action = "image_request"
        elif data_type == "log":
            action = "status_request"
        else:
            return None
        command = {
            "action": action,
            "targets": [target],
            "target_scope": "single",
            "params": params,
            "command_id": request.get("request_id") or make_msg_id("CMD", f"{action}_{target}"),
            "timeout_sec": as_float(request.get("timeout_sec"), as_float(self.config["defaults"].get("timeout"), 5.0)),
        }
        return self._adapt_control_command_request_v5_to_v4({**req, "mt": "control_command_request", "command": command})

    def _operator_response_v4_to_v5(
        self,
        response: Dict[str, Any],
        original_req: Dict[str, Any],
        mt_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        converted = dict(response)
        converted["v"] = FLEET_JSON_VERSION_V6
        converted["schema"] = FLEET_JSON_SCHEMA_V6
        converted["mt"] = mt_override or "operator_response"
        converted["ref"] = original_req.get("msg_id", converted.get("ref", ""))
        converted["source"] = "fleet_server"
        converted["dest"] = str(original_req.get("source", "control_ui"))
        converted.setdefault("msg_id", make_msg_id("MSG", converted["mt"]))
        converted.setdefault("ts", now_ts())
        if "message" not in converted and "st" in converted:
            converted["message"] = str(converted.get("st", ""))
        converted.setdefault("err", [])
        return converted

    def _operator_error_response_v5(
        self,
        req: Optional[Dict[str, Any]],
        code: str,
        msg: str,
        detail: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        source = str(req.get("source", "control_ui")) if isinstance(req, dict) else "control_ui"
        response = {
            "v": FLEET_JSON_VERSION_V6,
            "mt": "operator_response",
            "msg_id": make_msg_id("MSG", "operator_response_error"),
            "ref": req.get("msg_id", "") if isinstance(req, dict) else "",
            "ts": now_ts(),
            "source": "fleet_server",
            "dest": source,
            "schema": FLEET_JSON_SCHEMA_V6,
            "ok": False,
            "code": code,
            "message": msg,
            "command": {},
            "results": {},
            "err": [error_entry(code, msg, "fleet_server", detail)],
            "ui_hint": {
                "summary": msg,
                "severity": "error",
                "highlight_robots": [],
                "disable_buttons": ["start_mapping", "nav_goal"],
                "enable_buttons": ["status_request", "all_stop"],
            },
            "trace": {
                "request_msg_id": req.get("msg_id", "") if isinstance(req, dict) else "",
                "server_log_categories": ["operator_requests", "operator_responses"],
            },
        }
        self._save_log("operator_responses", "operator_response", response)
        self._print_response_summary(response)
        return response

    def _handle_control_health_request_v5(self, req: Dict[str, Any]) -> Dict[str, Any]:
        request = req.get("request", {})
        if not isinstance(request, dict):
            request = {}

        include_client_state = bool(request.get("include_client_state", True))
        include_robot_states = bool(request.get("include_robot_states", True))
        client_probe = self._send_client_heartbeat_v5() if include_client_state else {
            "connection_state": "UNKNOWN",
            "ok": None,
            "code": "R_SKIPPED",
            "message": "client_state probe skipped",
        }
        new_conn_state = client_probe.get("connection_state", "UNKNOWN")
        if new_conn_state != self._last_client_connection_state:
            self._last_client_connection_state = new_conn_state
            self._save_log("client_health", "client_heartbeat", client_probe)
        else:
            folder = self.log_base / "client_health"
            folder.mkdir(parents=True, exist_ok=True)
            save_json_file(folder / "latest_client_heartbeat.json", client_probe)

        robots: Dict[str, Any] = {}
        if include_robot_states:
            with self.state_lock:
                for robot_id, info in self.registry.get("robots", {}).items():
                    remembered = self.robot_states.get(robot_id, {})
                    enabled = bool(info.get("enabled", True))
                    connected = bool(remembered.get("connected", False))
                    robots[robot_id] = {
                        "enabled": enabled,
                        "connection_state": remembered.get("connection_state", "DISCONNECTED"),
                        "operating_mode": remembered.get("operating_mode", "MANUAL"),
                        "robot_state": remembered.get("robot_state", "DISCONNECTED" if enabled else "DISABLED"),
                        "job_state": remembered.get("job_state", "NONE"),
                        "accept_state": remembered.get("accept_state", "ACCEPTING" if connected else "BLOCKED"),
                        "ui_mode": remembered.get("ui_mode", "READY" if connected else "OFFLINE"),
                        "last_result": remembered.get("last_result", ""),
                        "last_seen": remembered.get("last_seen", ""),
                    }

        client_ok = client_probe.get("connection_state") == "CONNECTED" if include_client_state else True
        code = "R_HEALTH_OK" if client_ok else "R_HEALTH_WARN"
        response = {
            "v": FLEET_JSON_VERSION_V6,
            "mt": "control_health_response",
            "msg_id": make_msg_id("MSG", "control_health_response"),
            "ref": req.get("msg_id", ""),
            "ts": now_ts(),
            "source": "fleet_server",
            "dest": str(req.get("source", "control_ui")),
            "schema": FLEET_JSON_SCHEMA_V6,
            "ok": True,
            "code": code,
            "message": "fleet_server is alive" if client_ok else "fleet_server is alive; robot command client is not reachable",
            "server": {
                "server_time": now_ts(),
                "global_state": self.global_state,
                "uptime_sec": round(time.monotonic() - self.started_monotonic, 3),
                "public_ip": self.config["server"].get("public_ip", ""),
                "control_port": self._required_int(self.config["server"], "control_port", "server_config.server.control_port"),
                "control_health_port": self._control_ports()["health_port"],
                "control_command_port": self._control_ports()["command_port"],
                "control_data_port": self._control_ports()["data_control_port"],
                "client_event_port": self._control_ports()["client_event_port"],
            },
            "client": {
                "id": self._robot_command_client_id(),
                "ip": client_probe.get("ip"),
                "port": client_probe.get("port"),
                "health_port": self._robot_command_ports()["health_port"],
                "command_port": self._robot_command_ports()["command_port"],
                "data_control_port": self._robot_command_ports()["data_control_port"],
                "connection_state": client_probe.get("connection_state", "UNKNOWN"),
                "code": client_probe.get("code", ""),
                "message": client_probe.get("message", ""),
                "elapsed_ms": client_probe.get("elapsed_ms"),
            },
            "robots": robots,
            "err": [] if client_ok else [
                error_entry(
                    str(client_probe.get("code", "E_AGENT_DISCONNECTED")),
                    str(client_probe.get("message", "robot command client is not reachable")),
                    "fleet_server",
                    client_probe,
                )
            ],
        }
        self._save_log("operator_responses", "operator_response", response)
        self._print_response_summary(response)
        return response

    def _probe_robot_command_client_v5(self) -> Dict[str, Any]:
        agent_ip, agent_port = self._robot_command_address("health")
        timeout = min(float(self.config["server"].get("socket_timeout", 6.0)), 1.5)
        start = time.monotonic()
        probe: Dict[str, Any] = {
            "v": FLEET_JSON_VERSION_V6,
            "mt": "client_tcp_probe",
            "ts": now_ts(),
            "client_id": self._robot_command_client_id(),
            "ip": agent_ip,
            "port": agent_port,
            "timeout_sec": timeout,
            "ok": False,
            "connection_state": "DISCONNECTED",
            "code": "E_AGENT_DISCONNECTED",
            "message": "",
        }
        try:
            with socket.create_connection((agent_ip, agent_port), timeout=timeout):
                pass
            probe.update(
                {
                    "ok": True,
                    "connection_state": "CONNECTED",
                    "code": "R_CLIENT_TCP_CONNECTED",
                    "message": "robot command client TCP port is reachable",
                }
            )
        except socket.timeout as exc:
            probe.update(
                {
                    "code": "E_TIMEOUT",
                    "message": f"timed out while probing robot command client: {exc}",
                }
            )
        except OSError as exc:
            probe.update(
                {
                    "code": "E_AGENT_DISCONNECTED",
                    "message": f"failed to connect robot command client: {exc}",
                }
            )
        finally:
            probe["elapsed_ms"] = int((time.monotonic() - start) * 1000)
        return probe

    def _send_client_heartbeat_v5(self) -> Dict[str, Any]:
        agent_ip, agent_port = self._robot_command_address("health")
        timeout = min(float(self.config["server"].get("socket_timeout", 6.0)), 2.0)
        request = {
            "v": FLEET_JSON_VERSION_V6,
            "mt": "client_heartbeat_request",
            "msg_id": make_msg_id("MSG", "client_heartbeat_request"),
            "ts": now_ts(),
            "source": "fleet_server",
            "dest": self._robot_command_client_id(),
            "schema": FLEET_JSON_SCHEMA_V6,
            "request": {
                "include_robot_states": True,
                "robots": [
                    self._wire_robot_id(robot_id)
                    for robot_id, info in self.registry.get("robots", {}).items()
                    if bool(info.get("enabled", True))
                ],
            },
        }
        record: Dict[str, Any] = {
            "v": FLEET_JSON_VERSION_V6,
            "mt": "client_heartbeat",
            "ts": now_ts(),
            "request": request,
            "client_id": self._robot_command_client_id(),
            "ip": agent_ip,
            "port": agent_port,
            "timeout_sec": timeout,
            "ok": False,
            "connection_state": "DISCONNECTED",
            "code": "E_AGENT_DISCONNECTED",
            "message": "",
        }
        start = time.monotonic()
        try:
            with socket.create_connection((agent_ip, agent_port), timeout=timeout) as sock:
                sock.settimeout(timeout)
                send_json(sock, request)
                file_obj = sock.makefile("r", encoding="utf-8")
                response = recv_json_line(file_obj)
                if response is None:
                    raise ProtocolError("Robot command client closed connection before client_heartbeat_response")
        except socket.timeout as exc:
            record.update(
                {
                    "code": "E_TIMEOUT",
                    "message": f"timed out while heartbeat with robot command client: {exc}",
                }
            )
        except (OSError, ProtocolError) as exc:
            record.update(
                {
                    "code": "E_AGENT_DISCONNECTED",
                    "message": f"failed heartbeat with robot command client: {exc}",
                }
            )
        else:
            ok, code, msg = validate_client_heartbeat_response_v5(response)
            record["response"] = response
            if not ok:
                record.update(
                    {
                        "code": "E_BAD_REQUEST",
                        "message": msg,
                        "validator_code": code,
                    }
                )
            else:
                response_client = response.get("client", {})
                if not isinstance(response_client, dict):
                    response_client = {}
                connected = bool(response.get("ok")) and response_client.get("connection_state", "CONNECTED") == "CONNECTED"
                record.update(
                    {
                        "ok": bool(response.get("ok")),
                        "connection_state": "CONNECTED" if connected else "DISCONNECTED",
                        "code": response.get("code", "R_CLIENT_ALIVE" if connected else "E_AGENT_DISCONNECTED"),
                        "message": response.get("message", ""),
                        "client": response_client,
                        "robots": response.get("robots", {}),
                    }
                )
                robots = response.get("robots", {})
                if isinstance(robots, dict):
                    self._remember_client_robot_states_v5(robots)
        finally:
            record["elapsed_ms"] = int((time.monotonic() - start) * 1000)
        return record

    def _remember_client_robot_states_v5(self, robots: Dict[str, Any]) -> None:
        with self.state_lock:
            for robot_id, state in robots.items():
                if not isinstance(state, dict):
                    continue
                robot_key = self._canonical_robot_key(str(robot_id)) or str(robot_id)
                remembered = dict(self.robot_states.get(robot_key, {}))
                connected = state.get("connection_state") == "CONNECTED"
                remembered.update(
                    {
                        "reported_robot_id": str(robot_id),
                        "wire_robot_id": self._wire_robot_id(robot_key),
                        "state": state.get("ui_mode", "READY" if connected else "OFFLINE"),
                        "connected": connected,
                        "connection_state": state.get("connection_state", "CONNECTED" if connected else "DISCONNECTED"),
                        "operating_mode": state.get("operating_mode", "MANUAL"),
                        "robot_state": state.get("robot_state", "IDLE" if connected else "DISCONNECTED"),
                        "job_state": state.get("job_state", "NONE"),
                        "accept_state": state.get("accept_state", "ACCEPTING" if connected else "BLOCKED"),
                        "ui_mode": state.get("ui_mode", "READY" if connected else "OFFLINE"),
                        "last_seen": now_ts(),
                    }
                )
                self.robot_states[robot_key] = remembered

    def handle_operator_request_v4(self, req: Dict[str, Any], peer_ip: str) -> Dict[str, Any]:
        ok, code, msg = validate_operator_request_v4(req)
        if not ok:
            return self._operator_error_response_v4(req, code, msg)

        require_auth = bool(self.config.get("auth", {}).get("require_auth", False))
        auth_token = str(self.config.get("auth", {}).get("auth_token", "team_demo_token"))
        ok, code, msg = validate_auth(req, require_auth, auth_token)
        if not ok:
            return self._operator_error_response_v4(req, code, msg)

        command = req["command"]
        action = normalize_action(str(command.get("action", "")))
        policy = get_action_policy(self.action_policy, action)
        if policy is None:
            return self._operator_error_response_v4(
                req,
                "E_UNKNOWN_ACTION",
                f"No action policy for action: {action}",
            )

        target_scope = str(command.get("target_scope", ""))
        if target_scope not in policy.get("target_scope_allowed", []):
            return self._operator_error_response_v4(
                req,
                "E_TARGET_INVALID",
                f"{action} does not allow target_scope={target_scope}",
                {"target_scope_allowed": policy.get("target_scope_allowed", [])},
            )

        targets, target_err = self._resolve_targets_v4(target_scope, command.get("targets", []), action)
        if target_err is not None:
            return self._operator_error_response_v4(req, target_err[0], target_err[1], target_err[2])

        mode_ok, mode_code, mode_msg, mode_detail = self._check_policy_modes_v4(action, policy, targets)
        if not mode_ok:
            return self._operator_error_response_v4(req, mode_code, mode_msg, mode_detail)

        safety_ok, safety_code, safety_msg = self._check_server_safety(action, targets)
        if not safety_ok:
            return self._operator_error_response_v4(
                req,
                "E_SYSTEM_EMERGENCY" if safety_code == "E_SERVER_SAFETY_BLOCK" else "E_INTERNAL_ERROR",
                safety_msg,
                {"legacy_code": safety_code},
            )

        command_id = str(command.get("command_id", ""))
        with self.state_lock:
            if command_id in self.seen_command_ids:
                return self._operator_error_response_v4(
                    req,
                    "E_DUPLICATE_COMMAND",
                    f"duplicate command_id: {command_id}",
                )
            self.seen_command_ids.add(command_id)

        if action == "ping":
            return self._operator_ok_response_v4(req, "R_PONG", "pong", policy, targets, status=self._server_status_v4())

        if action in {"status_request", "robot_state_request", "job_status_request", "mapping_status", "map_status", "nav_status"}:
            return self._operator_ok_response_v4(req, "R_STATUS", "status", policy, targets, status=self._server_status_v4())

        if action == "map_list":
            return self._handle_map_list_v5(req, policy, targets)

        if action == "map_image_select":
            return self._handle_map_image_select_v5(req, policy, targets)

        if action == "image_request":
            return self._handle_image_request_v4(req, policy, targets)

        if action in {"image_view_closed", "file_cleanup_report"}:
            return self._handle_file_transfer_report_v4(req, action, policy, targets)

        job_id = str(command.get("job_id") or make_job_id(f"{action}_{'_'.join(targets)}"))
        results: Dict[str, Any] = {}
        fanout = len(targets) > 1 or target_scope == "all" or bool(command.get("group_id"))
        parent_command_id = str(command.get("command_id", ""))
        group_id = command.get("group_id")

        for robot_id in targets:
            server_command, build_err = self._build_server_command_v4(
                req=req,
                robot_id=robot_id,
                action=action,
                policy=policy,
                job_id=job_id,
                parent_command_id=parent_command_id,
                group_id=str(group_id) if group_id else None,
                fanout=fanout,
            )
            if build_err is not None:
                results[robot_id] = self._synthetic_agent_result_v4(
                    robot_id=robot_id,
                    command=None,
                    code=build_err[0],
                    msg=build_err[1],
                    detail=build_err[2],
                )
                continue
            result = self._send_server_command_to_agent_v4(robot_id, server_command)
            if action == "rsync_map" and bool(result.get("ok")):
                result = self._sync_map_from_client_v5(req, robot_id, result)
            elif action == "stop_mapping" and bool(result.get("ok")):
                result = self._sync_map_from_agent_result_v5(robot_id, result)
            results[robot_id] = result

        response = self._operator_response_from_results_v4(req, action, policy, job_id, targets, results)
        self._save_log("operator_responses", "operator_response", response)
        self._print_response_summary(response)
        return response

    def _resolve_targets_v4(
        self,
        target_scope: str,
        targets_value: Any,
        action: str,
    ) -> Tuple[List[str], Optional[Tuple[str, str, Dict[str, Any]]]]:
        robots = self.registry.get("robots", {})
        if not isinstance(targets_value, list) or not targets_value:
            return [], ("E_TARGET_INVALID", "targets must be a non-empty array", {"targets": targets_value})

        targets = [str(target).strip() for target in targets_value if str(target).strip()]
        if not targets:
            return [], ("E_TARGET_INVALID", "targets must contain at least one robot id", {"targets": targets_value})

        if target_scope == "all":
            if targets != ["all"]:
                return [], ("E_TARGET_INVALID", "target_scope=all requires targets=[\"all\"]", {"targets": targets})
            return [robot_id for robot_id, info in robots.items() if bool(info.get("enabled", True))], None

        if "all" in targets:
            return [], ("E_TARGET_INVALID", "targets may contain all only when target_scope=all", {"targets": targets})

        if target_scope == "single" and len(targets) != 1:
            return [], ("E_TARGET_INVALID", "target_scope=single requires exactly one target", {"targets": targets})

        resolved: List[str] = []
        for robot_id in targets:
            robot_key = self._canonical_robot_key(robot_id)
            if robot_key is None:
                return [], (
                    "E_TARGET_INVALID",
                    f"Unknown target robot_id: {robot_id}",
                    {"robot_id": robot_id, "known_targets": sorted(robots.keys())},
                )
            if not bool(robots[robot_key].get("enabled", True)):
                return [], ("E_TARGET_INVALID", f"Robot is disabled in registry: {robot_key}", {"robot_id": robot_id})
            if robot_key not in resolved:
                resolved.append(robot_key)

        if action in MOVE_ACTIONS and len(resolved) > 1 and not bool(self.config["safety"].get("allow_multi_robot_move", False)):
            return [], (
                "E_TARGET_INVALID",
                "multi robot move is blocked by server safety config",
                {"allow_multi_robot_move": False, "targets": resolved},
            )

        return resolved, None

    def _check_policy_modes_v4(
        self,
        action: str,
        policy: Dict[str, Any],
        targets: List[str],
    ) -> Tuple[bool, str, str, Dict[str, Any]]:
        if self.global_state == "EMERGENCY" and action not in {"emergency_stop", "all_stop", "status_request", "robot_state_request", "clear_emergency", "reset_all_jobs"}:
            return False, "E_SYSTEM_EMERGENCY", "global_state is EMERGENCY", {"global_state": self.global_state}

        allowed_modes = policy.get("allowed_operating_modes", [])
        if "ANY" in allowed_modes:
            return True, "R_ACCEPTED", "OK", {}

        modes_by_robot = {robot_id: self._robot_operating_mode(robot_id) for robot_id in targets}
        blocked = {robot_id: mode for robot_id, mode in modes_by_robot.items() if mode not in allowed_modes}
        if blocked:
            return (
                False,
                "E_MODE_BLOCKED",
                f"{action} is blocked by operating_mode",
                {"allowed_operating_modes": allowed_modes, "blocked": blocked},
            )
        return True, "R_ACCEPTED", "OK", {}

    def _robot_operating_mode(self, robot_id: str) -> str:
        with self.state_lock:
            remembered = self.robot_states.get(robot_id, {})
            mode = remembered.get("operating_mode")
        if mode:
            return str(mode)
        return "MANUAL"

    def _resolve_targets(self, target: str, action: str) -> Tuple[List[str], Optional[Tuple[str, str]]]:
        robots = self.registry.get("robots", {})

        if target == "all":
            if action in MOVE_ACTIONS and not bool(self.config["safety"].get("allow_multi_robot_move", False)):
                return [], (
                    "E_SERVER_MULTI_MOVE_BLOCKED",
                    "target=all is blocked for move actions. Use all_stop or enable allow_multi_robot_move.",
                )
            return [robot_id for robot_id, info in robots.items() if bool(info.get("enabled", True))], None

        robot_key = self._canonical_robot_key(target)
        if robot_key is None:
            return [], ("E_SERVER_INVALID_TARGET", f"Unknown target robot_id: {target}")

        if not bool(robots[robot_key].get("enabled", True)):
            return [], ("E_SERVER_INVALID_TARGET", f"Robot is disabled in registry: {robot_key}")

        return [robot_key], None

    def _build_server_command_v4(
        self,
        req: Dict[str, Any],
        robot_id: str,
        action: str,
        policy: Dict[str, Any],
        job_id: str,
        parent_command_id: str,
        group_id: Optional[str],
        fanout: bool,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Tuple[str, str, Dict[str, Any]]]]:
        robot_info = self.registry["robots"].get(robot_id)
        if not robot_info:
            return None, ("E_TARGET_INVALID", f"No client_info robot entry for {robot_id}", {"robot_id": robot_id})

        operator_command = req.get("command", {})
        if not isinstance(operator_command, dict):
            operator_command = {}

        params = operator_command.get("params", {})
        if not isinstance(params, dict):
            params = {}

        defaults = self.config["defaults"]
        timeout = as_float(operator_command.get("timeout_sec"), as_float(defaults.get("timeout"), 5.0))
        hz = as_int(params.get("hz"), as_int(defaults.get("hz"), 10))
        dur = as_float(params.get("dur"), as_float(defaults.get("dur"), 2.0))

        op = action
        command_params: Dict[str, Any]

        if action == "all_stop":
            op = "robot_stop"
        elif action == "stop":
            op = "robot_stop"

        if action == "move_forward":
            command_params = {
                "lx": abs(as_float(params.get("lx"), as_float(defaults.get("lx"), 0.05))),
                "az": 0.0,
                "dur": dur,
                "hz": hz,
                "stop": bool(params.get("stop", defaults.get("stop", True))),
            }
        elif action == "move_backward":
            command_params = {
                "lx": -abs(as_float(params.get("lx"), as_float(defaults.get("lx"), 0.05))),
                "az": 0.0,
                "dur": dur,
                "hz": hz,
                "stop": bool(params.get("stop", defaults.get("stop", True))),
            }
        elif action == "turn_left":
            command_params = {
                "lx": 0.0,
                "az": abs(as_float(params.get("az"), as_float(defaults.get("turn_az"), 0.5))),
                "dur": dur,
                "hz": hz,
                "stop": bool(params.get("stop", defaults.get("stop", True))),
            }
        elif action == "turn_right":
            command_params = {
                "lx": 0.0,
                "az": -abs(as_float(params.get("az"), as_float(defaults.get("turn_az"), 0.5))),
                "dur": dur,
                "hz": hz,
                "stop": bool(params.get("stop", defaults.get("stop", True))),
            }
        elif action == "custom_move":
            command_params = {
                "lx": as_float(params.get("lx"), as_float(defaults.get("lx"), 0.05)),
                "az": as_float(params.get("az"), as_float(defaults.get("az"), 0.0)),
                "dur": dur,
                "hz": hz,
                "stop": bool(params.get("stop", defaults.get("stop", True))),
            }
        elif action == "start_mapping":
            command_params = {
                "explore": bool(
                    params.get("explore")
                    or params.get("auto_explore")
                    or params.get("run_explorer")
                    or True
                ),
                "mapping_engine": str(params.get("mapping_engine", "cartographer")),
            }
            if params.get("map_name"):
                command_params["map_name"] = str(params["map_name"])
            if params.get("session_id"):
                command_params["session_id"] = str(params["session_id"])
            timeout = as_float(operator_command.get("timeout_sec"), 30.0)
        elif action == "stop_mapping":
            command_params = {"save": True}
            if params.get("map_name"):
                command_params["map_name"] = str(params["map_name"])
            if params.get("session_id"):
                command_params["session_id"] = str(params["session_id"])
            if params.get("format"):
                command_params["format"] = str(params["format"])
            timeout = as_float(operator_command.get("timeout_sec"), 60.0)
        elif op in {"robot_stop", "emergency_stop"}:
            command_params = {
                "lx": 0.0,
                "az": 0.0,
                "dur": as_float(params.get("dur"), 1.0),
                "hz": hz,
                "stop": True,
                "kill_explorer": True,
                "reason": params.get("reason", "operator_stop"),
            }
            if action == "all_stop":
                command_params["reason"] = params.get("reason", "all_stop_fanout")
            timeout = min(timeout, 5.0)
        else:
            command_params = dict(params)

        if action in MOVE_ACTIONS:
            param_err = self._validate_params("move_vel", command_params, timeout)
            if param_err is not None:
                return None, (self._map_legacy_error_code(param_err[0]), param_err[1], {"legacy_code": param_err[0]})

        child_policy = get_action_policy(self.action_policy, op) or policy
        wire_robot_id = self._wire_robot_id(robot_id)
        command_id = f"{parent_command_id}_{robot_id.upper()}" if fanout else parent_command_id
        agent_name = self._robot_command_client_id()
        topic = self._required_text(robot_info, "topic", f"client_info.robots.{robot_id}.topic")
        namespace = self._required_text(robot_info, "namespace", f"client_info.robots.{robot_id}.namespace")

        server_command = make_common_message(
            mt="server_command",
            source="fleet_server",
            dest=agent_name,
            msg_id=make_msg_id("MSG", f"server_command_{robot_id}"),
        )
        server_command["command"] = {
            "command_id": command_id,
            "parent_command_id": parent_command_id if fanout else None,
            "group_id": group_id,
            "job_id": job_id,
            "command_seq": operator_command.get("command_seq"),
            "command_revision": int(operator_command.get("command_revision", 0)),
            "op": op,
            "server_priority": int(child_policy.get("priority", policy.get("priority", 99))),
            "blocking_type": child_policy.get("blocking_type", policy.get("blocking_type", "SOFT")),
            "interrupt_policy": child_policy.get("interrupt_policy", policy.get("interrupt_policy", "reject_if_busy")),
            "robot_id": wire_robot_id,
            "ros": {
                "domain_id": robot_info.get("ros_domain_id"),
                "namespace": namespace,
                "topic": topic,
            },
            "params": command_params,
            "timeout_sec": timeout,
        }

        ok, code, msg = validate_server_command_v4(server_command)
        if not ok:
            return None, (code, msg, {"server_command": server_command})
        return server_command, None

    def _send_server_command_to_agent_v4(self, robot_id: str, command: Dict[str, Any]) -> Dict[str, Any]:
        agent_ip, agent_port = self._robot_command_address("command")
        agent_id = self._robot_command_client_id()
        wire_command = self._server_command_to_client_wire_v5(command)
        command_body = command.get("command", {})
        if not isinstance(command_body, dict):
            command_body = {}
        timeout = float(command_body.get("timeout_sec", self.config["server"].get("socket_timeout", 6.0)))

        self._save_log("commands", "server_command", wire_command)
        print(
            "[COMMAND OUT] "
            f"robot={robot_id} "
            f"client={agent_id} "
            f"addr={agent_ip}:{agent_port} "
            f"msg_id={wire_command.get('msg_id', '')} "
            f"command_id={command_body.get('command_id', '')} "
            f"op={command_body.get('op', '')}"
        )

        try:
            with socket.create_connection((agent_ip, agent_port), timeout=timeout) as sock:
                sock.settimeout(timeout)
                send_json(sock, wire_command)
                file_obj = sock.makefile("r", encoding="utf-8")
                result = recv_json_line(file_obj)
                if result is None:
                    raise ProtocolError("Robot agent closed connection before sending agent_result")
        except socket.timeout as exc:
            result = self._synthetic_agent_result_v4(
                robot_id=robot_id,
                command=wire_command,
                code="E_TIMEOUT",
                msg=f"Timed out while communicating with {agent_id}: {exc}",
                detail={"ip": agent_ip, "port": agent_port, "client_id": agent_id},
            )
            self._save_log("results", "agent_result", self._agent_result_to_log_v5(result))
            self._print_agent_result_v4(robot_id, result, source="server_synthetic")
            self._remember_robot_state_v4(robot_id, result)
            return result
        except (OSError, ProtocolError) as exc:
            result = self._synthetic_agent_result_v4(
                robot_id=robot_id,
                command=wire_command,
                code="E_AGENT_DISCONNECTED",
                msg=f"Failed to communicate with {agent_id}: {exc}",
                detail={"ip": agent_ip, "port": agent_port, "client_id": agent_id},
            )
            self._save_log("results", "agent_result", self._agent_result_to_log_v5(result))
            self._print_agent_result_v4(robot_id, result, source="server_synthetic")
            self._remember_robot_state_v4(robot_id, result)
            return result

        result = self._normalize_agent_result_for_internal_v4(result, wire_command, robot_id)
        ok, code, msg = validate_agent_result_v4(result)
        if not ok:
            result = self._synthetic_agent_result_v4(
                robot_id=robot_id,
                command=wire_command,
                code="E_BAD_REQUEST",
                msg=msg,
                detail={"received": result, "validator_code": code},
            )
        else:
            match_ok, match_msg = self._validate_agent_result_matches_command_v4(wire_command, result)
            if not match_ok:
                result = self._synthetic_agent_result_v4(
                    robot_id=robot_id,
                    command=wire_command,
                    code="E_STATE_MISMATCH",
                    msg=match_msg,
                    detail={"received": result},
                )

        self._save_log("results", "agent_result", self._agent_result_to_log_v5(result))
        self._print_agent_result_v4(robot_id, result)
        self._remember_robot_state_v4(robot_id, result)
        return result

    def _server_command_to_client_wire_v5(self, command: Dict[str, Any]) -> Dict[str, Any]:
        wire = dict(command)
        wire["v"] = FLEET_JSON_VERSION_V6
        wire["schema"] = FLEET_JSON_SCHEMA_V6
        wire["source"] = "fleet_server"
        wire["dest"] = self._robot_command_client_id()
        ok, code, msg = validate_server_command_v5(wire)
        if not ok:
            raise RuntimeError(f"Invalid v5 server_command ({code}): {msg}")
        return wire

    def _agent_result_to_log_v5(self, result: Dict[str, Any]) -> Dict[str, Any]:
        logged = dict(result)
        logged["v"] = FLEET_JSON_VERSION_V6
        logged["schema"] = FLEET_JSON_SCHEMA_V6
        logged.setdefault("mt", "agent_result")
        logged.setdefault("source", self._robot_command_client_id())
        logged.setdefault("dest", "fleet_server")
        return logged

    def _normalize_agent_result_for_internal_v4(
        self,
        result: Any,
        command: Dict[str, Any],
        robot_id: str,
    ) -> Dict[str, Any]:
        if not isinstance(result, dict):
            return {
                "v": FLEET_JSON_VERSION,
                "mt": "agent_result",
                "msg_id": make_msg_id("MSG", f"agent_result_{robot_id}"),
                "ref": command.get("msg_id", ""),
                "ts": now_ts(),
                "source": self._robot_command_client_id(),
                "dest": "fleet_server",
                "schema": FLEET_JSON_SCHEMA,
                "robot_id": robot_id,
                "command": {},
                "ok": False,
                "code": "E_BAD_REQUEST",
                "message": "agent_result must be a JSON object",
                "state": {},
                "perf": {},
                "err": [error_entry("E_BAD_REQUEST", "agent_result must be a JSON object", "fleet_server")],
            }

        normalized = dict(result)
        normalized["v"] = FLEET_JSON_VERSION
        normalized["schema"] = FLEET_JSON_SCHEMA
        normalized.setdefault("mt", "agent_result")
        normalized.setdefault("msg_id", make_msg_id("MSG", f"agent_result_{robot_id}"))
        normalized.setdefault("ref", command.get("msg_id", ""))
        normalized.setdefault("ts", now_ts())
        normalized.setdefault("source", self._robot_command_client_id())
        normalized.setdefault("dest", "fleet_server")
        command_body = command.get("command", {})
        if not isinstance(command_body, dict):
            command_body = {}
        normalized.setdefault("robot_id", command_body.get("robot_id") or robot_id)
        result_command = normalized.get("command")
        if not isinstance(result_command, dict):
            result_command = {}
        result_command.setdefault("command_id", command_body.get("command_id", ""))
        result_command.setdefault("parent_command_id", command_body.get("parent_command_id"))
        result_command.setdefault("group_id", command_body.get("group_id"))
        result_command.setdefault("job_id", command_body.get("job_id"))
        result_command.setdefault("op", command_body.get("op", ""))
        normalized["command"] = result_command

        ok_value = bool(normalized.get("ok"))
        raw_code = str(normalized.get("code", ""))
        code_aliases = {
            "OK": "R_DONE" if ok_value else "E_INTERNAL_ERROR",
            "R_OK": "R_DONE" if ok_value else "E_INTERNAL_ERROR",
            "DONE": "R_DONE",
            "ERROR": "E_INTERNAL_ERROR",
            "FAIL": "E_INTERNAL_ERROR",
            "FAILED": "E_INTERNAL_ERROR",
        }
        if raw_code in code_aliases:
            normalized["code"] = code_aliases[raw_code]
        normalized.setdefault("code", "R_DONE" if ok_value else "E_INTERNAL_ERROR")
        normalized.setdefault("message", f"{robot_id} {result_command.get('op', '')} result")

        state = normalized.get("state")
        if not isinstance(state, dict):
            state = {}
        state.setdefault("connection_state", "CONNECTED")
        state.setdefault("operating_mode", self._robot_operating_mode(robot_id))
        state.setdefault("robot_state", "IDLE" if ok_value else "ERROR")
        state.setdefault("job_state", "DONE" if ok_value else "FAILED")
        state.setdefault("accept_state", "ACCEPTING" if ok_value else "BLOCKED")
        state.setdefault("ui_mode", "READY" if ok_value else "ERROR")
        normalized["state"] = state

        if not isinstance(normalized.get("perf"), dict):
            normalized["perf"] = {"elapsed_ms": 0, "server_filled": True}
        if not isinstance(normalized.get("err"), list):
            normalized["err"] = []
        return normalized

    def _validate_agent_result_matches_command_v4(self, command: Dict[str, Any], result: Dict[str, Any]) -> Tuple[bool, str]:
        command_body = command.get("command", {})
        result_command = result.get("command", {})
        if not isinstance(command_body, dict) or not isinstance(result_command, dict):
            return False, "command bodies must be objects"

        checks = [
            (command.get("msg_id"), result.get("ref"), "server_command.msg_id != agent_result.ref"),
            (command_body.get("command_id"), result_command.get("command_id"), "command.command_id mismatch"),
            (command_body.get("op"), result_command.get("op"), "command.op mismatch"),
        ]
        expected_robot = str(command_body.get("robot_id", ""))
        actual_robot = str(result.get("robot_id", ""))
        if expected_robot != actual_robot:
            expected_key = self._canonical_robot_key(expected_robot)
            actual_key = self._canonical_robot_key(actual_robot)
            if expected_key is None or actual_key is None or expected_key != actual_key:
                return False, "server_command.robot_id != agent_result.robot_id"
        for expected, actual, message in checks:
            if expected != actual:
                return False, message
        return True, "OK"

    def _print_agent_result_v4(self, robot_id: str, result: Dict[str, Any], source: str = "agent") -> None:
        print(
            "[RESULT IN] "
            f"robot={robot_id} "
            f"ok={result.get('ok')} "
            f"code={result.get('code', '')} "
            f"msg_id={result.get('msg_id', '')} "
            f"source={source}"
        )

    def _build_heartbeat_request_v4(self, robot_id: str, include_state_report: bool = True) -> Dict[str, Any]:
        request = make_common_message(
            mt="heartbeat_request",
            source="fleet_server",
            dest=self._robot_command_client_id(),
            msg_id=make_msg_id("MSG", f"heartbeat_{robot_id}"),
        )
        request.update(
            {
                "robot_id": robot_id,
                "include_state_report": include_state_report,
            }
        )
        ok, code, msg = validate_heartbeat_request_v4(request)
        if not ok:
            raise RuntimeError(f"Invalid heartbeat_request ({code}): {msg}")
        return request

    def _send_heartbeat_to_agent_v4(
        self,
        robot_id: str,
        include_state_report: bool = True,
    ) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
        agent_ip, agent_port = self._robot_command_address("health")
        agent_id = self._robot_command_client_id()
        timeout = float(self.config["server"].get("socket_timeout", 6.0))
        request = self._build_heartbeat_request_v4(robot_id, include_state_report=include_state_report)

        self._save_log("heartbeats", "heartbeat_request", request)
        print(
            "[HEARTBEAT OUT] "
            f"robot={robot_id} "
            f"client={agent_id} "
            f"addr={agent_ip}:{agent_port} "
            f"msg_id={request.get('msg_id', '')}"
        )

        try:
            with socket.create_connection((agent_ip, agent_port), timeout=timeout) as sock:
                sock.settimeout(timeout)
                send_json(sock, request)
                file_obj = sock.makefile("r", encoding="utf-8")
                heartbeat_response = recv_json_line(file_obj)
                if heartbeat_response is None:
                    raise ProtocolError("Robot agent closed connection before heartbeat_response")

                state_report = None
                if include_state_report:
                    try:
                        state_report = recv_json_line(file_obj)
                    except socket.timeout:
                        state_report = None
        except socket.timeout as exc:
            heartbeat_response = self._synthetic_heartbeat_response_v4(
                robot_id,
                request,
                "E_TIMEOUT",
                f"Timed out while heartbeat with {agent_id}: {exc}",
            )
            state_report = None
        except (OSError, ProtocolError) as exc:
            heartbeat_response = self._synthetic_heartbeat_response_v4(
                robot_id,
                request,
                "E_AGENT_DISCONNECTED",
                f"Failed heartbeat with {agent_id}: {exc}",
            )
            state_report = None

        ok, code, msg = validate_heartbeat_response_v4(heartbeat_response)
        if not ok:
            heartbeat_response = self._synthetic_heartbeat_response_v4(
                robot_id,
                request,
                "E_BAD_REQUEST",
                msg,
                {"validator_code": code, "received": heartbeat_response},
            )
            state_report = None

        self._save_log("heartbeats", "heartbeat_response", heartbeat_response)
        print(
            "[HEARTBEAT IN] "
            f"robot={robot_id} "
            f"ok={heartbeat_response.get('ok')} "
            f"alive={heartbeat_response.get('agent_alive')} "
            f"code={heartbeat_response.get('code', '')}"
        )
        self._remember_heartbeat_v4(robot_id, heartbeat_response)

        if state_report is not None:
            ok, code, msg = validate_state_report_v4(state_report)
            if ok:
                self._save_log("state_reports", "state_report", state_report)
                self._remember_state_report_v4(robot_id, state_report)
                print(
                    "[STATE REPORT IN] "
                    f"robot={robot_id} "
                    f"state={state_report.get('state', {}).get('robot_state', '')}"
                )
            else:
                error_report = {
                    "robot_id": robot_id,
                    "code": code,
                    "message": msg,
                    "received": state_report,
                }
                self._save_log("state_reports", "state_report_invalid", error_report)
                state_report = None

        return heartbeat_response, state_report

    def _synthetic_heartbeat_response_v4(
        self,
        robot_id: str,
        request: Dict[str, Any],
        code: str,
        msg: str,
        detail: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        response = make_common_message(
            mt="heartbeat_response",
            source=self._robot_command_client_id(),
            dest="fleet_server",
            msg_id=make_msg_id("MSG", f"heartbeat_response_{robot_id}"),
        )
        response.update(
            {
                "ref": request.get("msg_id", ""),
                "robot_id": robot_id,
                "ok": False,
                "agent_alive": False,
                "code": code,
                "message": msg,
                "err": [
                    error_entry(code, msg, "fleet_server", detail),
                ],
            }
        )
        return response

    def _build_json_command(
        self,
        req: Dict[str, Any],
        robot_id: str,
        action: str,
        params: Dict[str, Any],
        job_id: str,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Tuple[str, str]]]:
        robot_info = self.registry["robots"].get(robot_id)
        if not robot_info:
            return None, ("E_SERVER_ROUTE_NOT_FOUND", f"No client_info robot entry for {robot_id}")

        defaults = self.config["defaults"]
        timeout = as_float(params.get("timeout"), as_float(defaults.get("timeout"), 5.0))
        hz = as_int(params.get("hz"), as_int(defaults.get("hz"), 10))
        dur = as_float(params.get("dur"), as_float(defaults.get("dur"), 2.0))

        op = "move_vel"
        p: Dict[str, Any]

        if action == "move_forward":
            p = {
                "lx": abs(as_float(params.get("lx"), as_float(defaults.get("lx"), 0.05))),
                "az": 0.0,
                "dur": dur,
                "hz": hz,
                "stop": bool(params.get("stop", defaults.get("stop", True))),
            }
        elif action == "move_backward":
            p = {
                "lx": -abs(as_float(params.get("lx"), as_float(defaults.get("lx"), 0.05))),
                "az": 0.0,
                "dur": dur,
                "hz": hz,
                "stop": bool(params.get("stop", defaults.get("stop", True))),
            }
        elif action == "turn_left":
            p = {
                "lx": 0.0,
                "az": abs(as_float(params.get("az"), as_float(defaults.get("turn_az"), 0.5))),
                "dur": dur,
                "hz": hz,
                "stop": bool(params.get("stop", defaults.get("stop", True))),
            }
        elif action == "turn_right":
            p = {
                "lx": 0.0,
                "az": -abs(as_float(params.get("az"), as_float(defaults.get("turn_az"), 0.5))),
                "dur": dur,
                "hz": hz,
                "stop": bool(params.get("stop", defaults.get("stop", True))),
            }
        elif action == "custom_move":
            p = {
                "lx": as_float(params.get("lx"), as_float(defaults.get("lx"), 0.05)),
                "az": as_float(params.get("az"), as_float(defaults.get("az"), 0.0)),
                "dur": dur,
                "hz": hz,
                "stop": bool(params.get("stop", defaults.get("stop", True))),
            }
        elif action in STOP_ACTIONS:
            op = "stop"
            p = {
                "lx": 0.0,
                "az": 0.0,
                "dur": as_float(params.get("dur"), 0.5),
                "hz": hz,
                "stop": True,
            }
            timeout = min(timeout, 2.0)
        else:
            return None, ("E_SERVER_UNSUPPORTED_ACTION", f"Unsupported action: {action}")

        param_err = self._validate_params(op, p, timeout)
        if param_err is not None:
            return None, param_err

        command = {
            "v": 3,
            "mt": "cmd",
            "id": self.ids.next("C", f"{op}_{robot_id}"),
            "ts": now_ts(),
            "job": job_id,
            "to": robot_id,
            "op": op,
            "ros": "topic",
            "topic": self._required_text(robot_info, "topic", f"client_info.robots.{robot_id}.topic"),
            "p": p,
            "lim": {
                "timeout": timeout,
            },
            "meta": {
                "operator_request": req.get("id", ""),
                "operator_action": action,
                "source": "fleet_server",
            },
        }

        ok, code, msg = validate_json_command_v03(command)
        if not ok:
            return None, (code, msg)
        return command, None

    def _validate_params(self, op: str, p: Dict[str, Any], timeout: float) -> Optional[Tuple[str, str]]:
        limits = self.config["limits"]
        lx_abs_max = float(limits.get("lx_abs_max", 0.10))
        az_abs_max = float(limits.get("az_abs_max", 1.0))
        dur_max = float(limits.get("dur_max", 5.0))
        hz_max = int(limits.get("hz_max", 50))
        timeout_max = float(limits.get("timeout_max", 10.0))

        lx = as_float(p.get("lx"), 0.0)
        az = as_float(p.get("az"), 0.0)
        dur = as_float(p.get("dur"), 0.0)
        hz = as_int(p.get("hz"), 0)

        if abs(lx) > lx_abs_max:
            return "E_PARAM_RANGE", f"abs(lx) must be <= {lx_abs_max}"
        if abs(az) > az_abs_max:
            return "E_PARAM_RANGE", f"abs(az) must be <= {az_abs_max}"
        if dur < 0.0 or dur > dur_max:
            return "E_PARAM_RANGE", f"dur must be between 0.0 and {dur_max}"
        if hz <= 0 or hz > hz_max:
            return "E_PARAM_RANGE", f"hz must be between 1 and {hz_max}"
        if timeout < dur or timeout > timeout_max:
            return "E_TIMEOUT_LIMIT", f"timeout must be >= dur and <= {timeout_max}"
        if op == "move_vel" and lx == 0.0 and az == 0.0:
            return "E_INVALID_PARAM", "move_vel must have non-zero lx or az. Use stop for zero velocity."
        return None

    def _send_command_to_agent(self, robot_id: str, command: Dict[str, Any]) -> Dict[str, Any]:
        agent_ip, agent_port = self._robot_command_address("command")
        agent_id = self._robot_command_client_id()
        timeout = float(command.get("lim", {}).get("timeout", self.config["server"].get("socket_timeout", 6.0)))

        self._save_log("commands", "json_command", command)
        print(
            "[COMMAND OUT] "
            f"robot={robot_id} "
            f"client={agent_id} "
            f"addr={agent_ip}:{agent_port} "
            f"id={command.get('id', '')} "
            f"op={command.get('op', '')}"
        )

        try:
            with socket.create_connection((agent_ip, agent_port), timeout=timeout) as sock:
                sock.settimeout(timeout)
                send_json(sock, command)
                file_obj = sock.makefile("r", encoding="utf-8")
                result = recv_json_line(file_obj)
                if result is None:
                    raise ProtocolError("Robot agent closed connection before sending json_result")
        except (OSError, ProtocolError) as exc:
            result = make_synthetic_result(
                command=command,
                result_id=self.ids.next("R", "SERVER_ERROR"),
                code="E_SERVER_CONNECT",
                msg=f"Failed to communicate with {agent_id}: {exc}",
                detail={"ip": agent_ip, "port": agent_port, "client_id": agent_id},
            )
            self._save_log("results", "json_result", result)
            print(
                "[RESULT IN] "
                f"robot={robot_id} "
                f"ok={result.get('ok')} "
                f"code={result.get('code', '')} "
                f"source=server_synthetic"
            )
            self._remember_robot_state(robot_id, result)
            return result

        ok, code, msg = validate_json_result_v03(result)
        if not ok:
            result = make_synthetic_result(
                command=command,
                result_id=self.ids.next("R", "BAD_RESULT"),
                code=code,
                msg=msg,
                detail={"received": result},
            )
        else:
            match_ok, match_msg = validate_result_matches_command(command, result)
            if not match_ok:
                result = make_synthetic_result(
                    command=command,
                    result_id=self.ids.next("R", "REF_MISMATCH"),
                    code="E_SERVER_REF_MISMATCH",
                    msg=match_msg,
                    detail={"received": result},
                )

        self._save_log("results", "json_result", result)
        print(
            "[RESULT IN] "
            f"robot={robot_id} "
            f"ok={result.get('ok')} "
            f"code={result.get('code', '')} "
            f"id={result.get('id', '')}"
        )
        self._remember_robot_state(robot_id, result)
        return result

    def _check_server_safety(self, action: str, targets: List[str]) -> Tuple[bool, str, str]:
        if action not in MOVE_ACTIONS:
            return True, "R_OK", "OK"

        event_path = resolve_path(self._required_text(self.config["safety"], "opencv_event_file", "server_config.safety.opencv_event_file"))
        if not event_path.exists():
            return True, "R_OK", "No opencv event file"

        try:
            event = load_required_json(event_path, "opencv_event_file")
        except Exception:
            return True, "R_OK", "Could not read opencv event file"

        lv = str(event.get("lv", "NORMAL")).upper()
        event_targets = event.get("targets", [])
        if not isinstance(event_targets, list):
            event_targets = []

        affects_target = not event_targets or any(robot_id in event_targets for robot_id in targets)
        if not affects_target:
            return True, "R_OK", "Safety event does not affect targets"

        if lv == "PAUSE" and bool(self.config["safety"].get("block_move_on_pause", True)):
            return False, "E_SERVER_SAFETY_BLOCK", "OpenCV event is PAUSE; move command blocked by server"
        if lv == "EMERGENCY" and bool(self.config["safety"].get("block_move_on_emergency", True)):
            return False, "E_SERVER_SAFETY_BLOCK", "OpenCV event is EMERGENCY; move command blocked by server"
        return True, "R_OK", "OK"

    def _local_error_result(
        self,
        robot_id: str,
        action: str,
        command: Optional[Dict[str, Any]],
        err: Tuple[str, str],
    ) -> Dict[str, Any]:
        if command is None:
            command = {
                "id": "",
                "job": "",
                "to": robot_id,
                "op": "move_vel" if action in MOVE_ACTIONS else "stop",
            }
        return make_synthetic_result(
            command=command,
            result_id=self.ids.next("R", "LOCAL_ERROR"),
            code=err[0],
            msg=err[1],
            where="fleet_server",
        )

    def _map_legacy_error_code(self, code: str) -> str:
        if code in {"E_PARAM_RANGE", "E_INVALID_PARAM"}:
            return "E_BAD_REQUEST"
        if code == "E_TIMEOUT_LIMIT":
            return "E_TIMEOUT"
        return "E_INTERNAL_ERROR"

    def _synthetic_agent_result_v4(
        self,
        robot_id: str,
        command: Optional[Dict[str, Any]],
        code: str,
        msg: str,
        detail: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        source = self._robot_command_client_id()
        command_body = command.get("command", {}) if isinstance(command, dict) else {}
        if not isinstance(command_body, dict):
            command_body = {}

        connection_state = "DISCONNECTED" if code in {"E_AGENT_DISCONNECTED", "E_TIMEOUT"} else "CONNECTED"
        robot_state = "DISCONNECTED" if connection_state == "DISCONNECTED" else "ERROR"
        ui_mode = "OFFLINE" if connection_state == "DISCONNECTED" else "READY"

        result = make_common_message(
            mt="agent_result",
            source=source,
            dest="fleet_server",
            msg_id=make_msg_id("MSG", f"agent_result_{robot_id}"),
        )
        result.update(
            {
                "ref": command.get("msg_id", "") if isinstance(command, dict) else "",
                "robot_id": robot_id,
                "command": {
                    "command_id": command_body.get("command_id", ""),
                    "parent_command_id": command_body.get("parent_command_id"),
                    "group_id": command_body.get("group_id"),
                    "job_id": command_body.get("job_id"),
                    "op": command_body.get("op", ""),
                },
                "ok": False,
                "code": code,
                "message": msg,
                "state": {
                    "connection_state": connection_state,
                    "operating_mode": self._robot_operating_mode(robot_id),
                    "robot_state": robot_state,
                    "job_state": "FAILED",
                    "accept_state": "BLOCKED",
                    "ui_mode": ui_mode,
                },
                "perf": {
                    "elapsed_ms": 0,
                    "server_synthetic": True,
                },
                "err": [
                    error_entry(code, msg, "fleet_server", detail),
                ],
            }
        )
        return result

    def _operator_response_from_results_v4(
        self,
        req: Dict[str, Any],
        action: str,
        policy: Dict[str, Any],
        job_id: str,
        targets: List[str],
        results: Dict[str, Any],
    ) -> Dict[str, Any]:
        command = req.get("command", {})
        if not isinstance(command, dict):
            command = {}

        ok_count = sum(1 for result in results.values() if isinstance(result, dict) and bool(result.get("ok")))
        total = len(results)
        failed_targets = [robot_id for robot_id, result in results.items() if not bool(result.get("ok"))]

        if total == 0:
            ok = False
            code = "E_INTERNAL_ERROR"
        elif ok_count == total:
            ok = True
            code = self._success_code_for_action_v4(action, results)
        elif ok_count == 0:
            ok = False
            code = self._failure_code_from_results_v4(results)
        else:
            ok = False
            code = "R_PARTIAL_SUCCESS"

        response = make_common_message(
            mt="operator_response",
            source="fleet_server",
            dest=str(req.get("source", "control_ui")),
            msg_id=make_msg_id("MSG", "operator_response"),
        )
        response.update(
            {
                "ref": req.get("msg_id", ""),
                "ok": ok,
                "code": code,
                "message": self._operator_message_v4(action, ok, code, failed_targets),
                "command": {
                    "command_id": command.get("command_id", ""),
                    "group_id": command.get("group_id"),
                    "job_id": job_id,
                    "action": command.get("action", action),
                    "normalized_action": action,
                    "server_priority": int(policy.get("priority", 99)),
                    "blocking_type": policy.get("blocking_type", ""),
                    "interrupt_policy": policy.get("interrupt_policy", ""),
                    "resolved_targets": targets,
                },
                "system": {
                    "global_state": self.global_state,
                },
                "results": {
                    robot_id: self._agent_result_to_ui_result(robot_id, result)
                    for robot_id, result in results.items()
                },
                "err": self._operator_errors_from_results_v4(results),
                "ui_hint": self._ui_hint_v4(action, ok, code, targets, failed_targets),
                "trace": {
                    "request_msg_id": req.get("msg_id", ""),
                    "command_id": command.get("command_id", ""),
                    "job_id": job_id,
                    "server_log_categories": [
                        "operator_requests",
                        "commands",
                        "results",
                        "operator_responses",
                    ],
                },
            }
        )

        if command.get("group_id") or len(targets) > 1 or action == "all_stop":
            response["group_result"] = {
                "group_id": command.get("group_id"),
                "total": total,
                "success": ok_count,
                "failed": total - ok_count,
                "status": "SUCCESS" if ok_count == total else "FAILED" if ok_count == 0 else "PARTIAL_SUCCESS",
            }

        return response

    def _agent_result_to_ui_result(self, robot_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(result, dict):
            return {
                "ok": False,
                "code": "E_INTERNAL_ERROR",
                "connection_state": "DISCONNECTED",
                "operating_mode": "MANUAL",
                "robot_state": "ERROR",
                "job_state": "FAILED",
                "accept_state": "BLOCKED",
                "ui_mode": "OFFLINE",
                "message": f"{robot_id} invalid result",
            }

        state = result.get("state", {})
        if not isinstance(state, dict):
            state = {}

        command = result.get("command", {})
        if not isinstance(command, dict):
            command = {}

        ui_result = {
            "ok": bool(result.get("ok")),
            "code": result.get("code", ""),
            "connection_state": state.get("connection_state", "CONNECTED" if result.get("ok") else "DISCONNECTED"),
            "operating_mode": state.get("operating_mode", self._robot_operating_mode(robot_id)),
            "robot_state": state.get("robot_state", "IDLE" if result.get("ok") else "ERROR"),
            "job_state": state.get("job_state", "DONE" if result.get("ok") else "FAILED"),
            "accept_state": state.get("accept_state", "ACCEPTING" if result.get("ok") else "BLOCKED"),
            "ui_mode": state.get("ui_mode", "READY" if result.get("ok") else "OFFLINE"),
            "message": result.get("message", ""),
            "agent_result_msg_id": result.get("msg_id", ""),
            "command_id": command.get("command_id", ""),
        }
        if result.get("err"):
            ui_result["err"] = result.get("err")
        return ui_result

    def _success_code_for_action_v4(self, action: str, results: Dict[str, Any]) -> str:
        if action in {"robot_stop", "all_stop", "emergency_stop"}:
            return "R_STOPPED"
        if action in {"pause_all", "pause_robot"}:
            return "R_PAUSED"
        if action in {"resume_all", "resume_robot"}:
            return "R_RESUMED"
        if action in {"cancel_job", "nav_cancel"}:
            return "R_CANCELED"
        codes = {str(result.get("code", "")) for result in results.values() if isinstance(result, dict)}
        if len(codes) == 1:
            only_code = next(iter(codes))
            if only_code.startswith("R_"):
                return only_code
        return "R_DONE"

    def _failure_code_from_results_v4(self, results: Dict[str, Any]) -> str:
        codes = [str(result.get("code", "")) for result in results.values() if isinstance(result, dict)]
        if codes and all(code == "E_AGENT_DISCONNECTED" for code in codes):
            return "E_AGENT_DISCONNECTED"
        if codes and all(code == "E_TIMEOUT" for code in codes):
            return "E_TIMEOUT"
        if len(codes) == 1 and codes[0].startswith("E_"):
            return codes[0]
        return "E_INTERNAL_ERROR"

    def _operator_errors_from_results_v4(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        err: List[Dict[str, Any]] = []
        for robot_id, result in results.items():
            if bool(result.get("ok")):
                continue
            err.append(
                error_entry(
                    str(result.get("code", "E_INTERNAL_ERROR")),
                    f"{robot_id}: {result.get('message', 'failed')}",
                    "fleet_server",
                    {"robot_id": robot_id, "agent_result_msg_id": result.get("msg_id", "")},
                )
            )
        return err

    def _operator_message_v4(self, action: str, ok: bool, code: str, failed_targets: List[str]) -> str:
        if ok:
            return f"{action} command completed"
        if code == "R_PARTIAL_SUCCESS":
            return f"{action} partially completed; failed targets: {', '.join(failed_targets)}"
        if failed_targets:
            return f"{action} failed for: {', '.join(failed_targets)}"
        return f"{action} rejected or failed"

    def _ui_hint_v4(
        self,
        action: str,
        ok: bool,
        code: str,
        targets: List[str],
        failed_targets: List[str],
    ) -> Dict[str, Any]:
        severity = "info" if ok else "warning" if code == "R_PARTIAL_SUCCESS" else "error"
        highlight = failed_targets if failed_targets else targets
        enable_buttons = ["status_request"]
        if action in MOVE_ACTIONS:
            enable_buttons.extend(["stop", "robot_stop"])
        elif action in {"robot_stop", "all_stop", "emergency_stop"}:
            enable_buttons.extend(["move_forward", "move_backward", "turn_left", "turn_right"])
        return {
            "summary": self._operator_message_v4(action, ok, code, failed_targets),
            "severity": severity,
            "highlight_robots": highlight,
            "disable_buttons": [] if ok else ["start_mapping", "nav_goal"],
            "enable_buttons": enable_buttons,
        }

    def _sync_map_from_client_v5(
        self,
        req: Dict[str, Any],
        robot_id: str,
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        command = req.get("command", {})
        if not isinstance(command, dict):
            command = {}
        params = command.get("params", {})
        if not isinstance(params, dict):
            params = {}

        sync_ok, code, message, transfer_record = self._request_and_land_client_map_v5(
            req=req,
            robot_id=robot_id,
            params=params,
        )

        updated = dict(result)
        updated["file_transfer"] = transfer_record
        if sync_ok:
            updated["code"] = "R_FILE_SYNC_REPORTED"
            updated["message"] = message
            return updated

        state = updated.get("state")
        if not isinstance(state, dict):
            state = {}
        state.update(
            {
                "robot_state": "ERROR",
                "job_state": "FAILED",
                "accept_state": "BLOCKED",
                "ui_mode": "ERROR",
            }
        )
        updated["state"] = state
        updated["ok"] = False
        updated["code"] = code
        updated["message"] = message
        err = updated.get("err")
        if not isinstance(err, list):
            err = []
        err.append(error_entry(code, message, "fleet_server", transfer_record))
        updated["err"] = err
        return updated

    def _request_and_land_client_map_v5(
        self,
        req: Dict[str, Any],
        robot_id: str,
        params: Dict[str, Any],
    ) -> Tuple[bool, str, str, Dict[str, Any]]:
        session_id = str(params.get("session_id") or make_msg_id("MAPSYNC", robot_id))
        request = self._build_client_data_prepare_request_v5(req, robot_id, session_id, params)
        response, comm_record = self._send_client_data_prepare_request_v5(request)
        transfer_record = {
            "v": FLEET_JSON_VERSION_V6,
            "schema": FLEET_JSON_SCHEMA_V6,
            "event": "client_map_sync",
            "ts": now_ts(),
            "session_id": session_id,
            "robot_id": robot_id,
            "wire_robot_id": self._wire_robot_id(robot_id),
            "request": request,
            "communication": comm_record,
            "ok": False,
        }
        if response is None:
            transfer_record["code"] = comm_record.get("code", "E_FILE_SYNC_FAILED")
            transfer_record["message"] = comm_record.get("message", "client data prepare failed")
            self._save_log("client_data", "client_map_sync", transfer_record)
            return False, str(transfer_record["code"]), str(transfer_record["message"]), transfer_record

        transfer_record["client_response"] = response
        if not bool(response.get("ok")):
            code = str(response.get("code", "E_FILE_SYNC_FAILED"))
            message = str(response.get("message", "client could not prepare map data"))
            transfer_record.update({"code": code, "message": message})
            self._save_log("client_data", "client_map_sync", transfer_record)
            return False, code, message, transfer_record

        land_ok, code, message, land_record = self._land_client_map_files_v5(robot_id, session_id, response)
        transfer_record["landing"] = land_record
        transfer_record.update({"ok": land_ok, "code": code, "message": message})
        self._save_log("client_data", "client_map_sync", transfer_record)
        return land_ok, code, message, transfer_record

    def _build_client_data_prepare_request_v5(
        self,
        req: Dict[str, Any],
        robot_id: str,
        session_id: str,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "v": FLEET_JSON_VERSION_V6,
            "mt": "client_data_prepare_request",
            "msg_id": make_msg_id("MSG", f"client_data_prepare_{robot_id}"),
            "ref": req.get("msg_id", ""),
            "ts": now_ts(),
            "source": "fleet_server",
            "dest": self._robot_command_client_id(),
            "schema": FLEET_JSON_SCHEMA_V6,
            "request": {
                "session_id": session_id,
                "action": "rsync_map",
                "data_type": "map",
                "robot_key": robot_id,
                "robot_id": self._wire_robot_id(robot_id),
                "preferred_files": ["map_image", "map_yaml", "map_metadata"],
                "params": params,
            },
        }

    def _send_client_data_prepare_request_v5(
        self,
        request: Dict[str, Any],
    ) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
        agent_ip, agent_port = self._robot_command_address("data_control")
        timeout = max(float(self.config["server"].get("socket_timeout", 6.0)), 15.0)
        record: Dict[str, Any] = {
            "v": FLEET_JSON_VERSION_V6,
            "mt": "client_data_prepare_exchange",
            "ts": now_ts(),
            "request_msg_id": request.get("msg_id", ""),
            "client_id": self._robot_command_client_id(),
            "ip": agent_ip,
            "port": agent_port,
            "timeout_sec": timeout,
            "ok": False,
        }
        self._save_log("client_data", "client_data_prepare_request", request)
        start = time.monotonic()
        try:
            with socket.create_connection((agent_ip, agent_port), timeout=timeout) as sock:
                sock.settimeout(timeout)
                send_json(sock, request)
                response = recv_json_line(sock.makefile("r", encoding="utf-8"))
                if response is None:
                    raise ProtocolError("Robot command client closed connection before client_data_prepare_response")
        except socket.timeout as exc:
            record.update({"code": "E_TIMEOUT", "message": f"timed out while preparing client map data: {exc}"})
            response = None
        except (OSError, ProtocolError) as exc:
            record.update({"code": "E_AGENT_DISCONNECTED", "message": f"failed client data prepare request: {exc}"})
            response = None
        else:
            response_ok, code, message = self._validate_client_data_prepare_response_v5(request, response)
            record.update(
                {
                    "ok": response_ok,
                    "code": code,
                    "message": message,
                    "response": response,
                }
            )
            if not response_ok:
                response = None
        finally:
            record["elapsed_ms"] = int((time.monotonic() - start) * 1000)
        if response is not None:
            self._save_log("client_data", "client_data_prepare_response", response)
        return response, record

    def _validate_client_data_prepare_response_v5(
        self,
        request: Dict[str, Any],
        response: Any,
    ) -> Tuple[bool, str, str]:
        if not isinstance(response, dict):
            return False, "E_BAD_REQUEST", "client_data_prepare_response must be a JSON object"
        if response.get("v") not in {FLEET_JSON_VERSION_V5, FLEET_JSON_VERSION_V6} or response.get("schema") not in FLEET_JSON_SCHEMA_V5_COMPAT:
            allowed = ", ".join(sorted(FLEET_JSON_SCHEMA_V5_COMPAT))
            return False, "E_BAD_REQUEST", f"client_data_prepare_response must use one of: {allowed}"
        if response.get("mt") != "client_data_prepare_response":
            return False, "E_BAD_REQUEST", "expected mt=client_data_prepare_response"
        if response.get("ref") != request.get("msg_id"):
            return False, "E_STATE_MISMATCH", "client_data_prepare_response.ref does not match request msg_id"
        if "ok" not in response or "code" not in response or "message" not in response:
            return False, "E_BAD_REQUEST", "client_data_prepare_response missing ok/code/message"
        return True, str(response.get("code", "R_ACCEPTED")), str(response.get("message", "OK"))

    def _land_client_map_files_v5(
        self,
        robot_id: str,
        session_id: str,
        response: Dict[str, Any],
    ) -> Tuple[bool, str, str, Dict[str, Any]]:
        landing_dir = self._client_map_landing_dir_v5(robot_id, session_id)
        landing_dir.mkdir(parents=True, exist_ok=True)
        files = self._client_data_files_v5(response)
        record: Dict[str, Any] = {
            "landing_dir": str(landing_dir),
            "files_requested": files,
            "received_files": [],
            "latest_image_path": "",
        }
        if not files:
            return False, "E_FILE_SYNC_FAILED", "client_data_prepare_response contained no files", record

        received: List[Path] = []
        transfer = response.get("transfer", {})
        if not isinstance(transfer, dict):
            transfer = {}
        method = str(transfer.get("method") or "local_copy")

        for index, file_info in enumerate(files):
            if not isinstance(file_info, dict):
                continue
            name = safe_file_name(file_info.get("name") or Path(str(file_info.get("path", ""))).name, f"client_file_{index}")
            target = landing_dir / name
            local_path = file_info.get("local_path") or file_info.get("path")
            if local_path and Path(str(local_path)).is_absolute() and Path(str(local_path)).exists():
                shutil.copy2(str(local_path), target)
            elif method == "rsync_over_ssh" or file_info.get("remote_path"):
                remote_path = str(file_info.get("remote_path") or file_info.get("path") or "").strip()
                if not remote_path:
                    return False, "E_FILE_SYNC_FAILED", "rsync file entry missing remote_path/path", record
                ok, code, msg, rsync_record = self._pull_client_file_rsync_v5(remote_path, target)
                record.setdefault("rsync", []).append(rsync_record)
                if not ok:
                    return False, code, msg, record
            else:
                return False, "E_FILE_SYNC_FAILED", "file entry must include local_path/path or remote_path for rsync", record

            received.append(target.resolve())
            record["received_files"].append(
                {
                    "path": str(target.resolve()),
                    "kind": file_info.get("kind", ""),
                    "bytes": target.stat().st_size,
                }
            )

        image = self._select_map_image_v5(received)
        if image is None:
            return False, "E_FILE_SYNC_FAILED", "received map files did not include an image", record

        latest_path = self._latest_map_image_path_v5(robot_id, image)
        latest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(image, latest_path)
        record["latest_image_path"] = str(latest_path.resolve())
        record["ok"] = True
        return True, "R_FILE_SYNC_REPORTED", f"map files received from client for {robot_id}", record

    def _client_data_files_v5(self, response: Dict[str, Any]) -> List[Any]:
        files = response.get("files")
        if isinstance(files, list):
            return files
        data = response.get("data", {})
        if isinstance(data, dict) and isinstance(data.get("files"), list):
            return data["files"]
        return []

    def _client_map_landing_dir_v5(self, robot_id: str, session_id: str) -> Path:
        client = self._robot_command_client()
        ssh = client.get("ssh", {})
        if not isinstance(ssh, dict):
            ssh = {}
        configured = str(ssh.get("map_server_dir") or "").strip()
        if not configured:
            paths = self._required_object(self.config, "paths", "server_config.paths")
            configured = self._required_text(paths, "server_transfer_from_client_dir", "server_config.paths.server_transfer_from_client_dir")
        return resolve_path(configured) / safe_file_name(robot_id, "robot") / safe_file_name(session_id, "session")

    def _pull_client_file_rsync_v5(self, remote_path: str, target: Path) -> Tuple[bool, str, str, Dict[str, Any]]:
        client = self._robot_command_client()
        ssh = client.get("ssh", {})
        if not isinstance(ssh, dict):
            ssh = {}
        if not bool(ssh.get("enabled", False)):
            return False, "E_FILE_SYNC_FAILED", "client_info.robot_command_client.ssh.enabled is false", {"remote_path": remote_path}
        user = str(ssh.get("user", "")).strip()
        host = str(ssh.get("ip") or client.get("ip") or "").strip()
        port = str(ssh.get("port", "22")).strip() or "22"
        connect_timeout = str(ssh.get("connect_timeout", "5")).strip() or "5"
        identity_file = str(ssh.get("identity_file", "")).strip()
        if not user or not host:
            return False, "E_FILE_SYNC_FAILED", "client ssh user/ip is required", {"remote_path": remote_path}
        target.parent.mkdir(parents=True, exist_ok=True)
        ssh_parts = [
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            f"ConnectTimeout={connect_timeout}",
            "-o",
            "StrictHostKeyChecking=accept-new",
        ]
        if port != "22":
            ssh_parts.extend(["-p", port])
        if identity_file:
            ssh_parts.extend(["-i", identity_file])
        ssh_command = " ".join(shlex.quote(part) for part in ssh_parts)
        source = f"{user}@{host}:{remote_path}"
        transfer_config = self._required_object(self.config, "file_transfer", "server_config.file_transfer")
        rsync_bin = self._required_text(transfer_config, "rsync_bin", "server_config.file_transfer.rsync_bin")
        timeout = float(transfer_config.get("rsync_timeout", 30.0))
        argv = [rsync_bin, "-az", "-e", ssh_command, "--", source, str(target)]
        start = time.monotonic()
        try:
            completed = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=False)
        except subprocess.TimeoutExpired as exc:
            return False, "E_TIMEOUT", f"rsync from client timed out after {timeout} seconds: {exc}", {
                "method": "rsync_over_ssh",
                "source": source,
                "target": str(target),
                "elapsed_ms": int((time.monotonic() - start) * 1000),
            }
        record = {
            "method": "rsync_over_ssh",
            "source": source,
            "target": str(target),
            "returncode": completed.returncode,
            "stdout": completed.stdout[-4000:],
            "stderr": completed.stderr[-4000:],
            "elapsed_ms": int((time.monotonic() - start) * 1000),
        }
        if completed.returncode != 0:
            return False, "E_FILE_SYNC_FAILED", f"rsync from client failed with returncode {completed.returncode}", record
        return True, "R_TRANSFER_DONE", "file pulled from client", record

    # ── map backup dir helpers ────────────────────────────────────────────────

    def _server_map_backup_dir(self) -> Path:
        paths = self._required_object(self.config, "paths", "server_config.paths")
        configured = self._required_text(paths, "server_map_backup_dir", "server_config.paths.server_map_backup_dir")
        return resolve_path(configured)

    def _client_map_save_dir(self) -> str:
        client = self._robot_command_client()
        paths = client.get("paths", {})
        if isinstance(paths, dict):
            val = str(paths.get("client_map_save_dir") or "").strip()
            if val:
                return val
        return ""

    def _parse_map_dir_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Parse YYYYMMDD_HHMMSS_robotName_saveMethod_saveNumber from a map directory name."""
        parts = name.split("_")
        if len(parts) < 5:
            return None
        date_str, time_str, robot, save_method = parts[0], parts[1], parts[2], parts[3]
        save_number_str = parts[4]
        if len(date_str) != 8 or not date_str.isdigit():
            return None
        if len(time_str) != 6 or not time_str.isdigit():
            return None
        if save_method not in ("autoSave", "stop", "emergency"):
            return None
        try:
            save_number = int(save_number_str)
        except ValueError:
            return None
        date_display = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
        time_display = f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:]}"
        return {
            "date": date_display,
            "time": time_display,
            "robot": robot,
            "save_method": save_method,
            "save_number": save_number,
        }

    def _list_server_map_dirs(self, robot_filter: str = "") -> List[Dict[str, Any]]:
        """List and parse all map directories on the server, optionally filtered by robot alias."""
        backup_dir = self._server_map_backup_dir()
        maps: List[Dict[str, Any]] = []
        if not backup_dir.exists() or not backup_dir.is_dir():
            return maps
        for d in sorted(backup_dir.iterdir()):
            if not d.is_dir():
                continue
            parsed = self._parse_map_dir_name(d.name)
            if parsed is None:
                continue
            if robot_filter and parsed["robot"].lower() != robot_filter.lower():
                continue
            files = sorted(f.name for f in d.iterdir() if f.is_file())
            parsed["dir_name"] = d.name
            parsed["files"] = files
            maps.append(parsed)
        for i, m in enumerate(maps, start=1):
            m["index"] = i
            m["display"] = f"{m['date']} {m['time']} | {m['robot']} | {m['save_method']} | #{m['save_number']}"
        return maps

    # ── auto map sync triggered by mapping_complete_notification ─────────────

    def _ssh_params_from_client(self) -> Tuple[str, str, str, str, str]:
        """Return (user, host, port, connect_timeout, identity_file) for client SSH."""
        client = self._robot_command_client()
        ssh = client.get("ssh", {})
        if not isinstance(ssh, dict):
            ssh = {}
        user = str(ssh.get("user", "")).strip()
        host = str(ssh.get("ip") or client.get("ip") or "").strip()
        port = str(ssh.get("port", "22")).strip() or "22"
        connect_timeout = str(ssh.get("connect_timeout", "5")).strip() or "5"
        identity_file = str(ssh.get("identity_file", "")).strip()
        return user, host, port, connect_timeout, identity_file

    def _build_ssh_command_parts(self, port: str, connect_timeout: str, identity_file: str) -> List[str]:
        parts = [
            "ssh",
            "-o", "BatchMode=yes",
            "-o", f"ConnectTimeout={connect_timeout}",
            "-o", "StrictHostKeyChecking=accept-new",
        ]
        if port != "22":
            parts.extend(["-p", port])
        if identity_file:
            parts.extend(["-i", identity_file])
        return parts

    def _pull_client_dir_rsync_v5(
        self,
        remote_dir: str,
        target_dir: Path,
    ) -> Tuple[bool, str, str, Dict[str, Any]]:
        """rsync-pull an entire directory from the client into target_dir."""
        client = self._robot_command_client()
        ssh = client.get("ssh", {})
        if not isinstance(ssh, dict):
            ssh = {}
        if not bool(ssh.get("enabled", False)):
            return False, "E_FILE_SYNC_FAILED", "client_info.robot_command_client.ssh.enabled is false", {"remote_dir": remote_dir}
        user, host, port, connect_timeout, identity_file = self._ssh_params_from_client()
        if not user or not host:
            return False, "E_FILE_SYNC_FAILED", "client ssh user/ip is required", {"remote_dir": remote_dir}

        target_dir.mkdir(parents=True, exist_ok=True)
        ssh_parts = self._build_ssh_command_parts(port, connect_timeout, identity_file)
        ssh_command = " ".join(shlex.quote(p) for p in ssh_parts)
        remote_source = f"{user}@{host}:{remote_dir.rstrip('/')}/"
        transfer_config = self._required_object(self.config, "file_transfer", "server_config.file_transfer")
        rsync_bin = self._required_text(transfer_config, "rsync_bin", "server_config.file_transfer.rsync_bin")
        timeout = float(transfer_config.get("rsync_timeout", 30.0))
        argv = [rsync_bin, "-az", "-e", ssh_command, "--", remote_source, str(target_dir) + "/"]
        record: Dict[str, Any] = {
            "method": "rsync_over_ssh",
            "remote_dir": remote_dir,
            "target_dir": str(target_dir),
            "argv": argv,
        }
        start = time.monotonic()
        try:
            completed = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=False)
        except subprocess.TimeoutExpired as exc:
            record["elapsed_ms"] = int((time.monotonic() - start) * 1000)
            return False, "E_TIMEOUT", f"rsync dir pull timed out: {exc}", record
        except FileNotFoundError:
            record["elapsed_ms"] = int((time.monotonic() - start) * 1000)
            return False, "E_FILE_SYNC_FAILED", f"rsync binary not found: {rsync_bin}", record
        record.update({
            "returncode": completed.returncode,
            "stdout": completed.stdout[-4000:],
            "stderr": completed.stderr[-4000:],
            "elapsed_ms": int((time.monotonic() - start) * 1000),
        })
        if completed.returncode != 0:
            return False, "E_FILE_SYNC_FAILED", f"rsync dir pull failed with returncode {completed.returncode}", record
        record["ok"] = True
        return True, "R_TRANSFER_DONE", f"directory pulled: {remote_dir}", record

    def _sync_map_from_agent_result_v5(self, robot_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        map_info = result.get("map", {})
        if not isinstance(map_info, dict):
            map_info = {}
        map_dir_name = str(map_info.get("map_dir_name") or "").strip()
        map_dir = str(map_info.get("map_dir") or "").strip()

        updated = dict(result)
        if not map_dir_name or not map_dir:
            updated.update({"ok": False, "code": "E_FILE_SYNC_FAILED",
                            "message": "stop_mapping result missing map.map_dir_name or map.map_dir"})
            return updated

        backup_dir = self._server_map_backup_dir()
        target_dir = backup_dir / safe_file_name(map_dir_name, "map")
        ok, code, message, transfer_record = self._pull_client_dir_rsync_v5(map_dir, target_dir)
        updated["file_transfer"] = transfer_record
        if ok:
            updated["code"] = "R_FILE_SYNC_REPORTED"
            updated["message"] = f"map synced from client: {map_dir_name}"
            print(f"[MAP SYNC] stop_mapping: {map_dir_name} -> {target_dir}")
        else:
            updated.update({"ok": False, "code": code, "message": message})
            print(f"[MAP SYNC] FAILED: {map_dir_name} code={code} message={message}")
        return updated

    def _auto_sync_map_from_client_v5(
        self,
        robot_alias: str,
        map_dir_name: str,
        client_map_dir: str,
    ) -> None:
        """Background: pull map directory from client after mapping_complete_notification."""
        backup_dir = self._server_map_backup_dir()
        target_dir = backup_dir / safe_file_name(map_dir_name, "map")

        log_record: Dict[str, Any] = {
            "v": FLEET_JSON_VERSION_V6,
            "schema": FLEET_JSON_SCHEMA_V6,
            "event": "auto_map_sync",
            "ts": now_ts(),
            "robot_alias": robot_alias,
            "map_dir_name": map_dir_name,
            "client_map_dir": client_map_dir,
            "target_dir": str(target_dir),
        }

        if target_dir.exists() and any(target_dir.iterdir()):
            log_record.update({"ok": True, "code": "R_FILE_SYNC_REPORTED", "message": "map directory already exists on server"})
            self._save_log("client_data", "auto_map_sync", log_record)
            print(f"[AUTO MAP SYNC] skipped (already exists): {map_dir_name}")
            return

        print(f"[AUTO MAP SYNC] pulling {map_dir_name} from client...")
        ok, code, message, transfer_record = self._pull_client_dir_rsync_v5(client_map_dir, target_dir)
        log_record.update({"ok": ok, "code": code, "message": message, "transfer": transfer_record})
        self._save_log("client_data", "auto_map_sync", log_record)

        if ok:
            print(f"[AUTO MAP SYNC] done: {map_dir_name} -> {target_dir}")
        else:
            print(f"[AUTO MAP SYNC] FAILED: {map_dir_name} code={code} message={message}")

    def _select_map_image_v5(self, paths: List[Path]) -> Optional[Path]:
        image_exts = {".png", ".jpg", ".jpeg", ".bmp", ".pgm"}
        images = [path for path in paths if path.suffix.lower() in image_exts and path.exists()]
        if not images:
            return None
        return max(images, key=lambda item: item.stat().st_mtime)

    def _latest_map_image_path_v5(self, robot_id: str, source_image: Path) -> Path:
        image_transfer = self._required_object(self.control_info, "image_transfer", "control_info.image_transfer")
        configured = str(image_transfer.get("default_server_path") or "").strip()
        if configured:
            return resolve_path(configured)
        transfer_config = self._required_object(self.config, "file_transfer", "server_config.file_transfer")
        image_dir = resolve_path(self._required_text(transfer_config, "server_image_dir", "server_config.file_transfer.server_image_dir"))
        return image_dir / f"{safe_file_name(robot_id, 'robot')}_latest_map{source_image.suffix.lower()}"

    # ── map list handler ──────────────────────────────────────────────────────

    def _handle_map_list_v5(
        self,
        req: Dict[str, Any],
        policy: Dict[str, Any],
        targets: List[str],
    ) -> Dict[str, Any]:
        command = req.get("command", {})
        if not isinstance(command, dict):
            command = {}
        params = command.get("params", {})
        if not isinstance(params, dict):
            params = {}
        robot_filter = str(params.get("robot") or "").strip()

        maps = self._list_server_map_dirs(robot_filter)
        status = {"maps": maps, "map_total": len(maps)}
        filter_desc = f" (robot={robot_filter})" if robot_filter else ""
        return self._operator_ok_response_v4(
            req,
            "R_STATUS",
            f"{len(maps)} maps found{filter_desc}",
            policy,
            targets,
            status=status,
        )

    # ── map image select handler ──────────────────────────────────────────────

    def _handle_map_image_select_v5(
        self,
        req: Dict[str, Any],
        policy: Dict[str, Any],
        targets: List[str],
    ) -> Dict[str, Any]:
        command = req.get("command", {})
        if not isinstance(command, dict):
            command = {}
        params = command.get("params", {})
        if not isinstance(params, dict):
            params = {}

        if not bool(self.config.get("file_transfer", {}).get("enabled", True)):
            return self._operator_error_response_v4(req, "E_FILE_SYNC_FAILED", "file_transfer is disabled by server config")

        index = params.get("index")
        dir_name = str(params.get("dir_name") or "").strip()
        backup_dir = self._server_map_backup_dir()

        if dir_name:
            selected_dir = backup_dir / dir_name
            if not selected_dir.exists() or not selected_dir.is_dir():
                return self._operator_error_response_v4(req, "E_FILE_SYNC_FAILED", f"map directory not found: {dir_name}")
        elif index is not None:
            all_maps = self._list_server_map_dirs()
            try:
                idx = int(index)
            except (ValueError, TypeError):
                return self._operator_error_response_v4(req, "E_BAD_REQUEST", "params.index must be a positive integer")
            if idx < 1 or idx > len(all_maps):
                return self._operator_error_response_v4(
                    req, "E_BAD_REQUEST", f"index {idx} out of range (1-{len(all_maps)})"
                )
            dir_name = all_maps[idx - 1]["dir_name"]
            selected_dir = backup_dir / dir_name
        else:
            return self._operator_error_response_v4(req, "E_BAD_REQUEST", "params must include index (integer) or dir_name (string)")

        ok, code, message, transfer_record = self._push_map_dir_to_control_v5(req, dir_name, selected_dir)
        self._save_log("file_transfers", "map_image_select", transfer_record)
        return self._operator_file_transfer_response_v4(
            req=req,
            action="map_image_select",
            policy=policy,
            targets=targets,
            ok=ok,
            code=code,
            message=message,
            transfer_record=transfer_record,
        )

    def _push_map_dir_to_control_v5(
        self,
        req: Dict[str, Any],
        dir_name: str,
        source_dir: Path,
    ) -> Tuple[bool, str, str, Dict[str, Any]]:
        """rsync push an entire map directory (yaml + pgm) from server to control."""
        command = req.get("command", {}) or {}
        transfer_defaults = self._control_image_transfer_defaults()
        control_host = str(transfer_defaults.get("control_host", "")).strip()
        control_user = str(transfer_defaults.get("control_user", "")).strip()
        ssh_port = str(transfer_defaults.get("ssh_port", "22")).strip() or "22"
        ssh_connect_timeout = str(transfer_defaults.get("ssh_connect_timeout", "5")).strip() or "5"
        identity_file = str(transfer_defaults.get("identity_file", "")).strip()

        control_ui = self._control_ui_info()
        paths = control_ui.get("paths", {})
        if not isinstance(paths, dict):
            paths = {}
        control_map_dir = str(paths.get("control_map_receive_dir") or "").strip()
        if not control_map_dir:
            return False, "E_BAD_REQUEST", "control_info.control_ui.paths.control_map_receive_dir is required", {}

        session_id = str(command.get("command_id") or make_msg_id("MAPSEND", dir_name))
        transfer_record: Dict[str, Any] = {
            "v": FLEET_JSON_VERSION_V6,
            "schema": FLEET_JSON_SCHEMA_V6,
            "event": "map_image_select",
            "ts": now_ts(),
            "session_id": session_id,
            "dir_name": dir_name,
            "source_dir": str(source_dir),
            "control_host": control_host,
            "control_user": control_user,
            "control_map_dir": control_map_dir,
            "ok": False,
        }

        for label, value in {"control_host": control_host, "control_user": control_user}.items():
            if not value or any(ch.isspace() for ch in value):
                return False, "E_BAD_REQUEST", f"{label} is required and must not contain whitespace", transfer_record

        if not ssh_port.isdigit():
            return False, "E_BAD_REQUEST", "ssh_port must be a number", transfer_record

        remote_dest = f"{control_user}@{control_host}:{control_map_dir.rstrip('/')}/{dir_name}/"
        ssh_parts = [
            "ssh",
            "-o", "BatchMode=yes",
            "-o", f"ConnectTimeout={ssh_connect_timeout}",
            "-o", "StrictHostKeyChecking=accept-new",
        ]
        if ssh_port != "22":
            ssh_parts.extend(["-p", ssh_port])
        if identity_file:
            ssh_parts.extend(["-i", identity_file])
        ssh_command = " ".join(shlex.quote(p) for p in ssh_parts)

        transfer_config = self.config.get("file_transfer", {})
        rsync_bin = str(transfer_config.get("rsync_bin", "rsync"))
        timeout = float(transfer_config.get("rsync_timeout", 30.0))
        argv = [rsync_bin, "-az", "-e", ssh_command, "--", str(source_dir) + "/", remote_dest]
        transfer_record.update({
            "rsync_argv": argv,
            "ssh_port": int(ssh_port),
            "ssh_connect_timeout": float(ssh_connect_timeout),
        })

        start = time.monotonic()
        try:
            completed = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=False)
        except FileNotFoundError:
            transfer_record["elapsed_ms"] = int((time.monotonic() - start) * 1000)
            return False, "E_FILE_SYNC_FAILED", f"rsync binary not found: {rsync_bin}", transfer_record
        except subprocess.TimeoutExpired as exc:
            transfer_record["elapsed_ms"] = int((time.monotonic() - start) * 1000)
            return False, "E_TIMEOUT", f"rsync timed out after {timeout} seconds", transfer_record

        transfer_record.update({
            "elapsed_ms": int((time.monotonic() - start) * 1000),
            "returncode": completed.returncode,
            "stdout": completed.stdout[-4000:],
            "stderr": completed.stderr[-4000:],
        })
        if completed.returncode != 0:
            return False, "E_FILE_SYNC_FAILED", f"rsync to control failed with returncode {completed.returncode}", transfer_record

        transfer_record["ok"] = True
        return True, "R_FILE_SYNC_REPORTED", f"map directory {dir_name} sent to control", transfer_record

    def _handle_image_request_v4(
        self,
        req: Dict[str, Any],
        policy: Dict[str, Any],
        targets: List[str],
    ) -> Dict[str, Any]:
        command = req.get("command", {})
        if not isinstance(command, dict):
            command = {}
        params = command.get("params", {})
        if not isinstance(params, dict):
            params = {}

        if not bool(self.config.get("file_transfer", {}).get("enabled", True)):
            return self._operator_error_response_v4(
                req,
                "E_FILE_SYNC_FAILED",
                "file_transfer is disabled by server config",
            )

        ok, code, message, transfer_record = self._run_image_rsync_v4(req, targets[0], params)
        self._save_log("file_transfers", "image_request", transfer_record)
        return self._operator_file_transfer_response_v4(
            req=req,
            action="image_request",
            policy=policy,
            targets=targets,
            ok=ok,
            code=code,
            message=message,
            transfer_record=transfer_record,
        )

    def _handle_file_transfer_report_v4(
        self,
        req: Dict[str, Any],
        action: str,
        policy: Dict[str, Any],
        targets: List[str],
    ) -> Dict[str, Any]:
        command = req.get("command", {})
        if not isinstance(command, dict):
            command = {}
        params = command.get("params", {})
        if not isinstance(params, dict):
            params = {}

        session_id = str(params.get("session_id", ""))
        transfer_record = {
            "v": FLEET_JSON_VERSION_V6,
            "schema": FLEET_JSON_SCHEMA_V6,
            "event": action,
            "ts": now_ts(),
            "request_msg_id": req.get("msg_id", ""),
            "command_id": command.get("command_id", ""),
            "session_id": session_id,
            "targets": targets,
            "closed_by": params.get("closed_by"),
            "displayed": params.get("displayed"),
            "local_path": params.get("local_path"),
            "local_file_deleted": params.get("local_file_deleted"),
            "params": params,
        }
        self._save_log("file_transfers", action, transfer_record)
        message = f"{action} reported"
        if session_id:
            message = f"{action} reported for {session_id}"
        return self._operator_file_transfer_response_v4(
            req=req,
            action=action,
            policy=policy,
            targets=targets,
            ok=True,
            code="R_FILE_SYNC_REPORTED",
            message=message,
            transfer_record=transfer_record,
        )

    def _run_image_rsync_v4(
        self,
        req: Dict[str, Any],
        robot_id: str,
        params: Dict[str, Any],
    ) -> Tuple[bool, str, str, Dict[str, Any]]:
        command = req.get("command", {})
        if not isinstance(command, dict):
            command = {}
        transfer = params.get("transfer", {})
        if not isinstance(transfer, dict):
            transfer = {}
        transfer_defaults = self._control_image_transfer_defaults()
        transfer = {
            "method": transfer_defaults.get("method", "rsync_over_ssh"),
            "direction": transfer_defaults.get("direction", "server_push"),
            "control_host": transfer_defaults.get("control_host", ""),
            "control_user": transfer_defaults.get("control_user", ""),
            "control_dir": transfer_defaults.get("control_dir", ""),
            "ssh_port": transfer_defaults.get("ssh_port", "22"),
            "ssh_connect_timeout": transfer_defaults.get("ssh_connect_timeout", "5"),
            "identity_file": transfer_defaults.get("identity_file", ""),
            **transfer,
        }
        params = dict(params)
        if not (params.get("server_path") or params.get("source_path") or params.get("image_path")):
            default_server_path = transfer_defaults.get("default_server_path", "")
            if default_server_path:
                params["server_path"] = default_server_path

        session_id = str(params.get("session_id") or make_msg_id("SYNC", f"image_{robot_id}"))
        transfer_record: Dict[str, Any] = {
            "v": FLEET_JSON_VERSION_V6,
            "schema": FLEET_JSON_SCHEMA_V6,
            "event": "image_request",
            "ts": now_ts(),
            "request_msg_id": req.get("msg_id", ""),
            "command_id": command.get("command_id", ""),
            "session_id": session_id,
            "robot_id": robot_id,
            "method": transfer.get("method", "rsync_over_ssh"),
            "direction": transfer.get("direction", "server_push"),
            "ok": False,
        }

        if transfer_record["method"] != "rsync_over_ssh":
            return False, "E_BAD_REQUEST", "transfer.method must be rsync_over_ssh", transfer_record
        if transfer_record["direction"] != "server_push":
            return False, "E_BAD_REQUEST", "transfer.direction must be server_push", transfer_record

        control_host = str(transfer.get("control_host", "")).strip()
        control_user = str(transfer.get("control_user", "")).strip()
        control_dir = str(transfer.get("control_dir", "")).strip()
        control_path = str(transfer.get("control_path", "")).strip()
        ssh_port = str(transfer.get("ssh_port", "22")).strip() or "22"
        ssh_connect_timeout = str(transfer.get("ssh_connect_timeout", "5")).strip() or "5"
        identity_file = str(transfer.get("identity_file", "")).strip()
        for label, value in {"control_host": control_host, "control_user": control_user}.items():
            if not value or any(ch.isspace() for ch in value) or "\n" in value or "\r" in value:
                return False, "E_BAD_REQUEST", f"transfer.{label} is required and must not contain whitespace", transfer_record
        if not ssh_port.isdigit():
            return False, "E_BAD_REQUEST", "transfer.ssh_port must be a number", transfer_record
        try:
            float(ssh_connect_timeout)
        except ValueError:
            return False, "E_BAD_REQUEST", "transfer.ssh_connect_timeout must be a number", transfer_record

        source_path, source_error = self._resolve_image_source_path_v4(robot_id, params)
        if source_error is not None:
            code, message, detail = source_error
            transfer_record["source_error"] = detail
            return False, code, message, transfer_record

        remote_path = control_path
        if not remote_path:
            if not control_dir:
                return False, "E_BAD_REQUEST", "transfer.control_dir or transfer.control_path is required", transfer_record
            remote_path = control_dir.rstrip("/") + "/" + source_path.name
        if not remote_path.startswith("/") or "\n" in remote_path or "\r" in remote_path:
            return False, "E_BAD_REQUEST", "transfer remote path must be an absolute path", transfer_record

        destination = f"{control_user}@{control_host}:{remote_path}"
        transfer_config = self.config.get("file_transfer", {})
        rsync_bin = str(transfer_config.get("rsync_bin", "rsync"))
        timeout = float(transfer_config.get("rsync_timeout", 30.0))
        ssh_command_parts = [
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            f"ConnectTimeout={ssh_connect_timeout}",
            "-o",
            "StrictHostKeyChecking=accept-new",
        ]
        if ssh_port != "22":
            ssh_command_parts.extend(["-p", ssh_port])
        if identity_file:
            ssh_command_parts.extend(["-i", identity_file])
        ssh_command = " ".join(shlex.quote(part) for part in ssh_command_parts)
        argv = [rsync_bin, "-az", "-e", ssh_command, "--", str(source_path), destination]

        transfer_record.update(
            {
                "source_path": str(source_path),
                "control_host": control_host,
                "control_user": control_user,
                "control_path": remote_path,
                "source_bytes": source_path.stat().st_size,
                "delete_after_view": bool(params.get("delete_after_view", True)),
                "ssh_port": int(ssh_port),
                "ssh_connect_timeout": float(ssh_connect_timeout),
                "identity_file": identity_file,
                "rsync_argv": argv,
            }
        )

        start = time.monotonic()
        try:
            completed = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except FileNotFoundError:
            transfer_record.update({"elapsed_ms": int((time.monotonic() - start) * 1000), "error": "rsync binary not found"})
            return False, "E_FILE_SYNC_FAILED", f"rsync binary not found: {rsync_bin}", transfer_record
        except subprocess.TimeoutExpired as exc:
            transfer_record.update({"elapsed_ms": int((time.monotonic() - start) * 1000), "error": str(exc)})
            return False, "E_TIMEOUT", f"rsync timed out after {timeout} seconds", transfer_record

        elapsed_ms = int((time.monotonic() - start) * 1000)
        transfer_record.update(
            {
                "elapsed_ms": elapsed_ms,
                "returncode": completed.returncode,
                "stdout": completed.stdout[-4000:],
                "stderr": completed.stderr[-4000:],
            }
        )
        if completed.returncode != 0:
            return False, "E_FILE_SYNC_FAILED", f"rsync failed with returncode {completed.returncode}", transfer_record

        transfer_record["ok"] = True
        return True, "R_FILE_SYNC_REPORTED", "image transferred to control computer", transfer_record

    def _resolve_image_source_path_v4(
        self,
        robot_id: str,
        params: Dict[str, Any],
    ) -> Tuple[Optional[Path], Optional[Tuple[str, str, Dict[str, Any]]]]:
        raw_path = params.get("server_path") or params.get("source_path") or params.get("image_path")
        if raw_path:
            source_path = resolve_path(str(raw_path)).resolve()
        else:
            source_path = self._find_latest_image_for_robot_v4(robot_id, params)
            if source_path is None:
                return None, (
                    "E_FILE_SYNC_FAILED",
                    "no image source path was provided and no latest image was found",
                    {"robot_id": robot_id},
                )

        if not source_path.exists() or not source_path.is_file():
            return None, (
                "E_FILE_SYNC_FAILED",
                "image source file does not exist",
                {"source_path": str(source_path)},
            )

        allowed_dirs = self._allowed_transfer_source_dirs_v4()
        if not any(self._path_is_relative_to_v4(source_path, allowed_dir) for allowed_dir in allowed_dirs):
            return None, (
                "E_BAD_REQUEST",
                "image source path is outside allowed_source_dirs",
                {"source_path": str(source_path), "allowed_source_dirs": [str(path) for path in allowed_dirs]},
            )
        return source_path, None

    def _allowed_transfer_source_dirs_v4(self) -> List[Path]:
        transfer_config = self._required_object(self.config, "file_transfer", "server_config.file_transfer")
        raw_dirs = transfer_config.get("allowed_source_dirs")
        if not isinstance(raw_dirs, list) or not raw_dirs:
            raise RuntimeError("server_config.file_transfer.allowed_source_dirs must be a non-empty list")
        return [resolve_path(str(path_text)).resolve() for path_text in raw_dirs]

    def _find_latest_image_for_robot_v4(self, robot_id: str, params: Dict[str, Any]) -> Optional[Path]:
        transfer_config = self._required_object(self.config, "file_transfer", "server_config.file_transfer")
        image_dir = resolve_path(self._required_text(transfer_config, "server_image_dir", "server_config.file_transfer.server_image_dir")).resolve()
        if not image_dir.exists() or not image_dir.is_dir():
            return None
        extensions = params.get("extensions", [".jpg", ".jpeg", ".png", ".bmp"])
        if not isinstance(extensions, list) or not extensions:
            extensions = [".jpg", ".jpeg", ".png", ".bmp"]
        allowed_exts = {str(ext).lower() if str(ext).startswith(".") else f".{str(ext).lower()}" for ext in extensions}
        image_type = str(params.get("image_type", "")).lower()
        candidates = []
        for path in image_dir.iterdir():
            if not path.is_file() or path.suffix.lower() not in allowed_exts:
                continue
            name = path.name.lower()
            if robot_id.lower() not in name:
                continue
            if image_type and image_type not in name:
                continue
            candidates.append(path)
        if not candidates:
            return None
        return max(candidates, key=lambda item: item.stat().st_mtime).resolve()

    def _path_is_relative_to_v4(self, path: Path, parent: Path) -> bool:
        try:
            path.resolve().relative_to(parent.resolve())
            return True
        except ValueError:
            return False

    def _operator_file_transfer_response_v4(
        self,
        req: Dict[str, Any],
        action: str,
        policy: Dict[str, Any],
        targets: List[str],
        ok: bool,
        code: str,
        message: str,
        transfer_record: Dict[str, Any],
    ) -> Dict[str, Any]:
        command = req.get("command", {})
        if not isinstance(command, dict):
            command = {}
        severity = "info" if ok else "error"
        response = make_common_message(
            mt="operator_response",
            source="fleet_server",
            dest=str(req.get("source", "control_ui")),
            msg_id=make_msg_id("MSG", f"{action}_response"),
        )
        response.update(
            {
                "ref": req.get("msg_id", ""),
                "ok": ok,
                "code": code,
                "message": message,
                "command": {
                    "command_id": command.get("command_id", ""),
                    "group_id": command.get("group_id"),
                    "job_id": command.get("job_id"),
                    "action": command.get("action", action),
                    "normalized_action": action,
                    "server_priority": int(policy.get("priority", 99)),
                    "blocking_type": policy.get("blocking_type", ""),
                    "interrupt_policy": policy.get("interrupt_policy", ""),
                    "resolved_targets": targets,
                },
                "system": {
                    "global_state": self.global_state,
                },
                "results": {
                    target: {
                        "ok": ok,
                        "code": code,
                        "message": message,
                        "file_transfer_session_id": transfer_record.get("session_id", ""),
                    }
                    for target in targets
                },
                "file_transfer": transfer_record,
                "err": [] if ok else [error_entry(code, message, "fleet_server", transfer_record)],
                "ui_hint": {
                    "summary": message,
                    "severity": severity,
                    "highlight_robots": targets,
                    "disable_buttons": [] if ok else ["image_request"],
                    "enable_buttons": ["status_request"],
                },
                "trace": {
                    "request_msg_id": req.get("msg_id", ""),
                    "command_id": command.get("command_id", ""),
                    "server_log_categories": ["operator_requests", "file_transfers", "operator_responses"],
                },
            }
        )
        self._save_log("operator_responses", "operator_response", response)
        self._print_response_summary(response)
        return response

    def _operator_ok_response_v4(
        self,
        req: Dict[str, Any],
        code: str,
        message: str,
        policy: Dict[str, Any],
        targets: List[str],
        status: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        command = req.get("command", {})
        if not isinstance(command, dict):
            command = {}
        action = normalize_action(str(command.get("action", "")))

        response = make_common_message(
            mt="operator_response",
            source="fleet_server",
            dest=str(req.get("source", "control_ui")),
            msg_id=make_msg_id("MSG", "operator_response"),
        )
        response.update(
            {
                "ref": req.get("msg_id", ""),
                "ok": True,
                "code": code,
                "message": message,
                "command": {
                    "command_id": command.get("command_id", ""),
                    "group_id": command.get("group_id"),
                    "job_id": command.get("job_id"),
                    "action": command.get("action", action),
                    "normalized_action": action,
                    "server_priority": int(policy.get("priority", 99)),
                    "blocking_type": policy.get("blocking_type", ""),
                    "interrupt_policy": policy.get("interrupt_policy", ""),
                    "resolved_targets": targets,
                },
                "system": {
                    "global_state": self.global_state,
                },
                "results": self._status_results_v4(targets, code),
                "err": [],
                "ui_hint": {
                    "summary": message,
                    "severity": "info",
                    "highlight_robots": targets,
                    "disable_buttons": [],
                    "enable_buttons": ["status_request"],
                },
                "trace": {
                    "request_msg_id": req.get("msg_id", ""),
                    "command_id": command.get("command_id", ""),
                    "server_log_categories": ["operator_requests", "operator_responses"],
                },
            }
        )
        if status is not None:
            response["status"] = status
        self._save_log("operator_responses", "operator_response", response)
        self._print_response_summary(response)
        return response

    def _operator_error_response_v4(
        self,
        req: Optional[Dict[str, Any]],
        code: str,
        msg: str,
        detail: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        source = "control_ui"
        command: Dict[str, Any] = {}
        if isinstance(req, dict):
            source = str(req.get("source", "control_ui"))
            raw_command = req.get("command", {})
            if isinstance(raw_command, dict):
                command = raw_command
        action = normalize_action(str(command.get("action", "")))
        policy = get_action_policy(self.action_policy, action) if action else None

        response = make_common_message(
            mt="operator_response",
            source="fleet_server",
            dest=source,
            msg_id=make_msg_id("MSG", "operator_response_error"),
        )
        response.update(
            {
                "ref": req.get("msg_id", "") if isinstance(req, dict) else "",
                "ok": False,
                "code": code,
                "message": msg,
                "command": {
                    "command_id": command.get("command_id", ""),
                    "group_id": command.get("group_id"),
                    "job_id": command.get("job_id"),
                    "action": command.get("action", ""),
                    "normalized_action": action,
                    "server_priority": int(policy.get("priority", 0)) if isinstance(policy, dict) else 0,
                    "blocking_type": policy.get("blocking_type", "") if isinstance(policy, dict) else "",
                    "interrupt_policy": policy.get("interrupt_policy", "") if isinstance(policy, dict) else "",
                    "resolved_targets": [],
                },
                "system": {
                    "global_state": self.global_state,
                },
                "results": {},
                "err": [
                    error_entry(code, msg, "fleet_server", detail),
                ],
                "ui_hint": {
                    "summary": msg,
                    "severity": "error",
                    "highlight_robots": [],
                    "disable_buttons": ["start_mapping", "nav_goal"],
                    "enable_buttons": ["status_request", "all_stop"],
                },
                "trace": {
                    "request_msg_id": req.get("msg_id", "") if isinstance(req, dict) else "",
                    "command_id": command.get("command_id", ""),
                    "server_log_categories": ["operator_requests", "operator_responses"],
                },
            }
        )
        self._save_log("operator_responses", "operator_response", response)
        self._print_response_summary(response)
        return response

    def _operator_response_from_results(
        self,
        req: Dict[str, Any],
        job_id: str,
        results: Dict[str, Any],
    ) -> Dict[str, Any]:
        ok_count = sum(1 for result in results.values() if bool(result.get("ok")))
        total = len(results)

        if total == 0:
            ok = False
            st = "failed"
            code = "E_INTERNAL"
        elif ok_count == total:
            ok = True
            st = "done"
            code = "R_OK"
        elif ok_count == 0:
            ok = False
            st = "failed"
            code = "E_SERVER_ROUTE_FAILED"
        else:
            ok = False
            st = "partial"
            code = "E_SERVER_PARTIAL_RESULT"

        err = []
        for robot_id, result in results.items():
            if not bool(result.get("ok")):
                err.append(
                    error_entry(
                        str(result.get("code", "E_INTERNAL")),
                        f"{robot_id}: {result.get('st', 'failed')}",
                        "fleet_server",
                        {"result_id": result.get("id"), "robot_id": robot_id},
                    )
                )

        return {
            "v": 1,
            "mt": "operator_response",
            "id": self.ids.next("OR"),
            "ref": req.get("id", ""),
            "ts": now_ts(),
            "job": job_id,
            "target": req.get("target", ""),
            "action": req.get("action", ""),
            "ok": ok,
            "st": st,
            "code": code,
            "results": results,
            "err": err,
            "trace": {
                "request_id": req.get("id", ""),
                "job": job_id,
                "result_codes": {
                    robot_id: result.get("code", "")
                    for robot_id, result in results.items()
                    if isinstance(result, dict)
                },
                "server_log_categories": [
                    "operator_requests",
                    "commands",
                    "results",
                    "operator_responses",
                ],
            },
        }

    def _operator_ok_response(
        self,
        req: Dict[str, Any],
        code: str,
        st: str,
        status: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        response = {
            "v": 1,
            "mt": "operator_response",
            "id": self.ids.next("OR"),
            "ref": req.get("id", ""),
            "ts": now_ts(),
            "job": "",
            "target": req.get("target", ""),
            "action": req.get("action", ""),
            "ok": True,
            "st": st,
            "code": code,
            "results": {},
            "err": [],
        }
        if status is not None:
            response["status"] = status
        response["trace"] = {
            "request_id": req.get("id", ""),
            "server_log_categories": ["operator_requests", "operator_responses"],
        }
        self._save_log("operator_responses", "operator_response", response)
        self._print_response_summary(response)
        return response

    def _operator_error_response(
        self,
        req: Optional[Dict[str, Any]],
        code: str,
        msg: str,
        detail: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        response = {
            "v": 1,
            "mt": "operator_response",
            "id": self.ids.next("OR"),
            "ref": req.get("id", "") if isinstance(req, dict) else "",
            "ts": now_ts(),
            "job": "",
            "target": req.get("target", "") if isinstance(req, dict) else "",
            "action": req.get("action", "") if isinstance(req, dict) else "",
            "ok": False,
            "st": "rejected",
            "code": code,
            "results": {},
            "err": [
                error_entry(code, msg, "fleet_server", detail),
            ],
            "trace": {
                "request_id": req.get("id", "") if isinstance(req, dict) else "",
                "server_log_categories": ["operator_responses"],
            },
        }
        self._save_log("operator_responses", "operator_response", response)
        self._print_response_summary(response)
        return response

    def _remember_robot_state(self, robot_id: str, result: Dict[str, Any]) -> None:
        state = "READY" if result.get("ok") else "FAILED"
        if result.get("st") in {"unsafe", "timeout"}:
            state = str(result.get("st", "FAILED")).upper()
        with self.state_lock:
            self.robot_states[robot_id] = {
                "state": state,
                "connected": bool(result.get("ok")),
                "last_result": result.get("code", ""),
                "last_result_id": result.get("id", ""),
                "last_seen": now_ts(),
            }

    def _remember_robot_state_v4(self, robot_id: str, result: Dict[str, Any]) -> None:
        result_state = result.get("state", {})
        if not isinstance(result_state, dict):
            result_state = {}
        with self.state_lock:
            self.robot_states[robot_id] = {
                "state": result_state.get("ui_mode", "READY" if result.get("ok") else "OFFLINE"),
                "connected": result_state.get("connection_state") == "CONNECTED" if result_state else bool(result.get("ok")),
                "connection_state": result_state.get("connection_state", "CONNECTED" if result.get("ok") else "DISCONNECTED"),
                "operating_mode": result_state.get("operating_mode", "MANUAL"),
                "robot_state": result_state.get("robot_state", "IDLE" if result.get("ok") else "ERROR"),
                "job_state": result_state.get("job_state", "DONE" if result.get("ok") else "FAILED"),
                "accept_state": result_state.get("accept_state", "ACCEPTING" if result.get("ok") else "BLOCKED"),
                "ui_mode": result_state.get("ui_mode", "READY" if result.get("ok") else "OFFLINE"),
                "last_result": result.get("code", ""),
                "last_result_msg_id": result.get("msg_id", ""),
                "last_seen": now_ts(),
            }

    def _remember_heartbeat_v4(self, robot_id: str, heartbeat_response: Dict[str, Any]) -> None:
        alive = bool(heartbeat_response.get("ok")) and bool(heartbeat_response.get("agent_alive"))
        with self.state_lock:
            remembered = dict(self.robot_states.get(robot_id, {}))
            remembered.update(
                {
                    "state": "READY" if alive else "OFFLINE",
                    "connected": alive,
                    "connection_state": "CONNECTED" if alive else "DISCONNECTED",
                    "operating_mode": remembered.get("operating_mode", "MANUAL"),
                    "robot_state": remembered.get("robot_state", "IDLE" if alive else "DISCONNECTED"),
                    "job_state": remembered.get("job_state", "NONE"),
                    "accept_state": remembered.get("accept_state", "ACCEPTING" if alive else "BLOCKED"),
                    "ui_mode": remembered.get("ui_mode", "READY" if alive else "OFFLINE"),
                    "last_heartbeat_code": heartbeat_response.get("code", ""),
                    "last_heartbeat_msg_id": heartbeat_response.get("msg_id", ""),
                    "last_seen": now_ts(),
                }
            )
            self.robot_states[robot_id] = remembered

    def _remember_state_report_v4(self, robot_id: str, state_report: Dict[str, Any]) -> None:
        state = state_report.get("state", {})
        if not isinstance(state, dict):
            state = {}
        with self.state_lock:
            remembered = dict(self.robot_states.get(robot_id, {}))
            connected = state.get("connection_state") == "CONNECTED"
            remembered.update(
                {
                    "state": state.get("ui_mode", "READY" if connected else "OFFLINE"),
                    "connected": connected,
                    "connection_state": state.get("connection_state", "CONNECTED" if connected else "DISCONNECTED"),
                    "operating_mode": state.get("operating_mode", "MANUAL"),
                    "robot_state": state.get("robot_state", "IDLE" if connected else "DISCONNECTED"),
                    "job_state": state.get("job_state", "NONE"),
                    "accept_state": state.get("accept_state", "ACCEPTING" if connected else "BLOCKED"),
                    "ui_mode": state.get("ui_mode", "READY" if connected else "OFFLINE"),
                    "battery_level": state.get("battery_level"),
                    "current_job": state_report.get("current_job"),
                    "last_state_report_msg_id": state_report.get("msg_id", ""),
                    "last_seen": now_ts(),
                }
            )
            self.robot_states[robot_id] = remembered

    def _status_results_v4(self, targets: List[str], code: str) -> Dict[str, Any]:
        if not targets:
            targets = [robot_id for robot_id, info in self.registry.get("robots", {}).items() if bool(info.get("enabled", True))]
        results: Dict[str, Any] = {}
        client_ip, client_port = self._robot_command_address("command")
        client_ports = self._robot_command_ports()
        client_id = self._robot_command_client_id()
        with self.state_lock:
            for robot_id in targets:
                info = self.registry.get("robots", {}).get(robot_id, {})
                remembered = self.robot_states.get(robot_id, {})
                connected = bool(remembered.get("connected", False))
                results[robot_id] = {
                    "ok": True,
                    "code": code,
                    "connection_state": remembered.get("connection_state", "CONNECTED" if connected else "DISCONNECTED"),
                    "operating_mode": remembered.get("operating_mode", "MANUAL"),
                    "robot_state": remembered.get("robot_state", "IDLE" if connected else "DISCONNECTED"),
                    "job_state": remembered.get("job_state", "NONE"),
                    "accept_state": remembered.get("accept_state", "ACCEPTING" if connected else "BLOCKED"),
                    "ui_mode": remembered.get("ui_mode", "READY" if connected else "OFFLINE"),
                    "message": f"{robot_id} status",
                    "enabled": bool(info.get("enabled", True)),
                    "command_client_id": client_id,
                    "command_client_ip": client_ip,
                    "command_client_port": client_port,
                    "health_client_port": client_ports["health_port"],
                    "data_control_client_port": client_ports["data_control_port"],
                    "last_result": remembered.get("last_result", ""),
                    "last_seen": remembered.get("last_seen", ""),
                }
        return results

    def _server_status(self) -> Dict[str, Any]:
        robots = {}
        client_ip, client_port = self._robot_command_address("command")
        client_ports = self._robot_command_ports()
        client_id = self._robot_command_client_id()
        with self.state_lock:
            for robot_id, info in self.registry.get("robots", {}).items():
                remembered = self.robot_states.get(robot_id, {})
                robots[robot_id] = {
                    "state": remembered.get("state", "UNKNOWN"),
                    "connected": remembered.get("connected", False),
                    "enabled": bool(info.get("enabled", True)),
                    "command_client_id": client_id,
                    "command_client_ip": client_ip,
                    "command_client_port": client_port,
                    "health_client_port": client_ports["health_port"],
                    "data_control_client_port": client_ports["data_control_port"],
                    "topic": info.get("topic", ""),
                    "last_result": remembered.get("last_result", ""),
                    "last_seen": remembered.get("last_seen", ""),
                }
        return {
            "v": 1,
            "mt": "server_status",
            "ts": now_ts(),
            "server": {
                "name": self.config["server"].get("name", "fleet_server"),
                "state": "READY",
                "public_ip": self.config["server"].get("public_ip", ""),
                "control_port": self._required_int(self.config["server"], "control_port", "server_config.server.control_port"),
                "control_health_port": self._control_ports()["health_port"],
                "control_command_port": self._control_ports()["command_port"],
                "control_data_port": self._control_ports()["data_control_port"],
            },
            "robot_command_client": self._robot_command_client(),
            "robots": robots,
        }

    def _server_status_v4(self) -> Dict[str, Any]:
        robots = {}
        client_ip, client_port = self._robot_command_address("command")
        client_ports = self._robot_command_ports()
        client_id = self._robot_command_client_id()
        with self.state_lock:
            for robot_id, info in self.registry.get("robots", {}).items():
                remembered = self.robot_states.get(robot_id, {})
                connected = bool(remembered.get("connected", False))
                robots[robot_id] = {
                    "connection_state": remembered.get("connection_state", "CONNECTED" if connected else "DISCONNECTED"),
                    "operating_mode": remembered.get("operating_mode", "MANUAL"),
                    "robot_state": remembered.get("robot_state", "IDLE" if connected else "DISCONNECTED"),
                    "job_state": remembered.get("job_state", "NONE"),
                    "accept_state": remembered.get("accept_state", "ACCEPTING" if connected else "BLOCKED"),
                    "ui_mode": remembered.get("ui_mode", "READY" if connected else "OFFLINE"),
                    "enabled": bool(info.get("enabled", True)),
                    "command_client_id": client_id,
                    "command_client_ip": client_ip,
                    "command_client_port": client_port,
                    "health_client_port": client_ports["health_port"],
                    "data_control_client_port": client_ports["data_control_port"],
                    "topic": info.get("topic", ""),
                    "last_result": remembered.get("last_result", ""),
                    "last_seen": remembered.get("last_seen", ""),
                }
        return {
            "v": FLEET_JSON_VERSION_V6,
            "schema": FLEET_JSON_SCHEMA_V6,
            "mt": "server_status",
            "ts": now_ts(),
            "global_state": self.global_state,
            "server": {
                "name": self.config["server"].get("name", "fleet_server"),
                "state": "READY",
                "public_ip": self.config["server"].get("public_ip", ""),
                "control_port": self._required_int(self.config["server"], "control_port", "server_config.server.control_port"),
                "control_health_port": self._control_ports()["health_port"],
                "control_command_port": self._control_ports()["command_port"],
                "control_data_port": self._control_ports()["data_control_port"],
            },
            "robot_command_client": self._robot_command_client(),
            "robots": robots,
        }

    def _archive_log_session(self, retention_days: int = 7) -> None:
        latest_dir = self.log_base
        if not latest_dir.exists():
            return
        has_files = any(f for f in latest_dir.rglob("*.json") if f.is_file())
        if not has_files:
            return
        events_dir = latest_dir.parent / "events"
        events_dir.mkdir(parents=True, exist_ok=True)
        session_name = f"session_{time.strftime('%Y%m%d_%H%M%S')}"
        session_dir = events_dir / session_name
        try:
            shutil.copytree(str(latest_dir), str(session_dir))
        except Exception as exc:
            print(f"[LOG] archive failed: {exc}")
            return
        for item in latest_dir.iterdir():
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
            except Exception:
                pass
        cutoff = time.time() - retention_days * 86400
        for old_session in events_dir.iterdir():
            if old_session.is_dir() and old_session != session_dir:
                try:
                    if old_session.stat().st_mtime < cutoff:
                        shutil.rmtree(old_session)
                        print(f"[LOG] purged old session: {old_session.name}")
                except Exception:
                    pass

    def _log_shutdown(self, reason: str = "unexpected") -> None:
        status = {
            "v": FLEET_JSON_VERSION_V6,
            "mt": "server_shutdown_check",
            "schema": FLEET_JSON_SCHEMA_V6,
            "ts": now_ts(),
            "reason": reason,
            "uptime_sec": round(time.monotonic() - self.started_monotonic, 3),
        }
        self._save_log("system", "shutdown_check", status)

    def _log_startup(self) -> None:
        self._archive_log_session()
        status = {
            "v": FLEET_JSON_VERSION_V6,
            "mt": "server_startup_check",
            "schema": FLEET_JSON_SCHEMA_V6,
            "ts": now_ts(),
            "config_path": str(self.config_path),
            "client_info_path": str(self.client_info_path),
            "control_info_path": str(self.control_info_path),
            "action_policy_path": str(self.action_policy_path),
            "local_ip_candidates": get_local_ip_candidates(),
            "server": self.config.get("server", {}),
            "robot_command_client": self._robot_command_client(),
            "control_ui": self._control_ui_info(),
            "robots": self.registry.get("robots", {}),
        }
        self._save_log("system", "startup_check", status)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TurtleBot fleet communication server")
    parser.add_argument(
        "--config",
        default=str(SCRIPT_DIR.parent / "json" / "server_config.json"),
        help="Path to server_config.json",
    )
    parser.add_argument("--bind-ip", default="", help="Override server.bind_ip")
    parser.add_argument("--public-ip", default="", help="Override server.public_ip")
    parser.add_argument("--health-port", type=int, default=0, help="Override server.control_health_port")
    parser.add_argument("--command-port", type=int, default=0, help="Override server.control_command_port")
    parser.add_argument("--data-port", type=int, default=0, help="Override server.control_data_port")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = FleetServer(Path(args.config).resolve())
    if args.bind_ip:
        server.config["server"]["bind_ip"] = args.bind_ip
    if args.public_ip:
        server.config["server"]["public_ip"] = args.public_ip
    if args.health_port:
        server.config["server"]["control_port"] = args.health_port
        server.config["server"]["control_health_port"] = args.health_port
    if args.command_port:
        server.config["server"]["control_command_port"] = args.command_port
    if args.data_port:
        server.config["server"]["control_data_port"] = args.data_port
    server.run()


if __name__ == "__main__":
    main()
