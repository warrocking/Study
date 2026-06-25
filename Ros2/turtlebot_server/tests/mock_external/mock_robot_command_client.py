import argparse
import socket
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
CODE_DIR = SCRIPT_DIR.parents[1] / "program" / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from fleet_protocol import (
    FLEET_JSON_VERSION,
    FLEET_JSON_VERSION_V5,
    IdGenerator,
    ProtocolError,
    error_entry,
    make_common_message,
    make_common_message_v5,
    make_msg_id,
    now_ts,
    recv_json_line,
    send_json,
    validate_agent_result_v4,
    validate_agent_result_v5,
    validate_client_heartbeat_response_v5,
    validate_heartbeat_request_v4,
    validate_heartbeat_response_v4,
    validate_json_command_v03,
    validate_server_command_v4,
    validate_server_command_v5,
    validate_state_report_v4,
)


DEFAULT_GATEWAY_PORT = 5000
DEFAULT_COMMAND_PORT = 5001
DEFAULT_DATA_CONTROL_PORT = 5002
KNOWN_ROBOTS = {"tb1", "14", "tb3_1", "tb3_2", "tb3_3"}
MOCK_PNG_BYTES = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010802000000907753de"
    "0000000c49444154789c6360f8cf00000301010118dd8db00000000049454e44ae426082"
)


ids = IdGenerator()

MOVE_OPS = {"move_forward", "move_backward", "turn_left", "turn_right", "custom_move"}
STOP_OPS = {"robot_stop", "emergency_stop"}
PAUSE_OPS = {"pause_all", "pause_robot"}
RESUME_OPS = {"resume_all", "resume_robot"}
CANCEL_OPS = {"cancel_job", "nav_cancel"}
STATUS_OPS = {"status_request", "robot_state_request", "job_status_request", "ping", "mapping_status", "map_status", "map_list", "nav_status"}
BACKGROUND_OPS = {"start_mapping", "stop_mapping", "save_map", "rsync_map", "nav_goal", "clear_error", "clear_emergency", "reset_all_jobs"}


def make_legacy_result(command: Dict[str, Any], robot_id: str, ok: bool, st: str, code: str, err: list[Dict[str, Any]]) -> Dict[str, Any]:
    p = command.get("p", {})
    dur = float(p.get("dur", 0.0) or 0.0)
    hz = int(p.get("hz", 10) or 10)
    pub = max(0, int(dur * hz))
    return {
        "v": 3,
        "mt": "res",
        "id": ids.next("R", robot_id),
        "ref": command.get("id", ""),
        "ts": now_ts(),
        "job": command.get("job", ""),
        "from": robot_id,
        "op": command.get("op", ""),
        "ok": ok,
        "st": st,
        "code": code,
        "perf": {
            "dur": dur,
            "pub": pub,
            "mock": True,
        },
        "err": err,
    }


def command_body_v4(command: Dict[str, Any]) -> Dict[str, Any]:
    body = command.get("command", {})
    if isinstance(body, dict):
        return body
    return {}


def source_for_robot(robot_id: str) -> str:
    return f"client_{robot_id}"


def base_ready_state() -> Dict[str, Any]:
    return {
        "connection_state": "CONNECTED",
        "operating_mode": "MANUAL",
        "robot_state": "IDLE",
        "job_state": "NONE",
        "accept_state": "ACCEPTING",
        "ui_mode": "READY",
        "battery_level": None,
    }


def make_heartbeat_response_v4(request: Dict[str, Any], robot_id: str, ok: bool = True, agent_alive: bool = True) -> Dict[str, Any]:
    response = make_common_message(
        mt="heartbeat_response",
        source=str(request.get("dest") or source_for_robot(robot_id)),
        dest="fleet_server",
        msg_id=make_msg_id("MSG", f"heartbeat_response_{robot_id}"),
    )
    response.update(
        {
            "ref": request.get("msg_id", ""),
            "robot_id": robot_id,
            "ok": ok,
            "agent_alive": agent_alive,
            "state": base_ready_state(),
        }
    )
    return response


def make_state_report_v4(robot_id: str, ref: str = "", state: Dict[str, Any] | None = None, source: str = "") -> Dict[str, Any]:
    report = make_common_message(
        mt="state_report",
        source=source or source_for_robot(robot_id),
        dest="fleet_server",
        msg_id=make_msg_id("MSG", f"state_report_{robot_id}"),
    )
    report.update(
        {
            "ref": ref,
            "robot_id": robot_id,
            "state": state or base_ready_state(),
            "current_job": {
                "job_id": None,
                "action": None,
                "started_at": None,
            },
        }
    )
    return report


def handle_heartbeat_request_v4(request: Dict[str, Any], robot_id: str) -> Tuple[Dict[str, Any], Dict[str, Any] | None]:
    valid, code, msg = validate_heartbeat_request_v4(request)
    if not valid:
        response = make_heartbeat_response_v4(request, robot_id, ok=False, agent_alive=False)
        response["code"] = "E_BAD_REQUEST"
        response["message"] = msg
        return response, None

    requested_robot_id = str(request.get("robot_id", ""))
    if requested_robot_id not in {robot_id, "all"}:
        response = make_heartbeat_response_v4(request, robot_id, ok=False, agent_alive=False)
        response["code"] = "E_TARGET_INVALID"
        response["message"] = f"Mock agent controls {robot_id}, but heartbeat target is {requested_robot_id}"
        return response, None

    response = make_heartbeat_response_v4(request, robot_id, ok=True, agent_alive=True)
    response["code"] = "R_PONG"
    response["message"] = f"{robot_id} heartbeat ok"
    state_report = None
    if bool(request.get("include_state_report", False)):
        state_report = make_state_report_v4(robot_id, ref=request.get("msg_id", ""), source=str(response.get("source", "")))

    valid_response, response_code, response_msg = validate_heartbeat_response_v4(response)
    if not valid_response:
        response = make_heartbeat_response_v4(request, robot_id, ok=False, agent_alive=False)
        response["code"] = "E_INTERNAL_ERROR"
        response["message"] = f"mock generated invalid heartbeat_response: {response_msg}"
        response["detail"] = {"validator_code": response_code}
        return response, None

    if state_report is not None:
        valid_report, report_code, report_msg = validate_state_report_v4(state_report)
        if not valid_report:
            response["ok"] = False
            response["agent_alive"] = False
            response["code"] = "E_INTERNAL_ERROR"
            response["message"] = f"mock generated invalid state_report: {report_msg}"
            response["detail"] = {"validator_code": report_code}
            return response, None

    return response, state_report


def make_agent_result_v4(
    server_command: Dict[str, Any],
    robot_id: str,
    ok: bool,
    code: str,
    message: str,
    state: Dict[str, Any],
    perf: Dict[str, Any],
    err: Any = None,
) -> Dict[str, Any]:
    body = command_body_v4(server_command)
    result = make_common_message(
        mt="agent_result",
        source=str(server_command.get("dest", source_for_robot(robot_id))),
        dest="fleet_server",
        msg_id=make_msg_id("MSG", f"agent_result_{robot_id}"),
    )
    result.update(
        {
            "ref": server_command.get("msg_id", ""),
            "robot_id": robot_id,
            "command": {
                "command_id": body.get("command_id", ""),
                "parent_command_id": body.get("parent_command_id"),
                "group_id": body.get("group_id"),
                "job_id": body.get("job_id"),
                "op": body.get("op", ""),
            },
            "ok": ok,
            "code": code,
            "message": message,
            "state": state,
            "perf": perf,
            "err": err,
        }
    )
    return result


def make_agent_result_v5(
    server_command: Dict[str, Any],
    robot_id: str,
    ok: bool,
    code: str,
    message: str,
    state: Dict[str, Any],
    perf: Dict[str, Any],
    err: Any = None,
) -> Dict[str, Any]:
    body = command_body_v4(server_command)
    result = make_common_message_v5(
        mt="agent_result",
        source=str(server_command.get("dest", "robot_command_client")),
        dest="fleet_server",
        msg_id=make_msg_id("MSG", f"agent_result_{robot_id}"),
    )
    result.update(
        {
            "ref": server_command.get("msg_id", ""),
            "robot_id": robot_id,
            "command": {
                "command_id": body.get("command_id", ""),
                "parent_command_id": body.get("parent_command_id"),
                "group_id": body.get("group_id"),
                "job_id": body.get("job_id"),
                "op": body.get("op", ""),
            },
            "ok": ok,
            "code": code,
            "message": message,
            "state": state,
            "perf": perf,
            "err": err or [],
        }
    )
    return result


def make_error_agent_result_v5(
    server_command: Dict[str, Any],
    robot_id: str,
    code: str,
    message: str,
    detail: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return make_agent_result_v5(
        server_command,
        robot_id,
        ok=False,
        code=code,
        message=message,
        state={
            "connection_state": "CONNECTED",
            "operating_mode": "MANUAL",
            "robot_state": "ERROR",
            "job_state": "REJECTED",
            "accept_state": "BLOCKED",
            "ui_mode": "ERROR",
        },
        perf={
            "elapsed_ms": 0,
            "mock": True,
        },
        err=[error_entry(code, message, f"mock_{robot_id}", detail)],
    )


def make_error_agent_result_v4(
    server_command: Dict[str, Any],
    robot_id: str,
    code: str,
    message: str,
    detail: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return make_agent_result_v4(
        server_command,
        robot_id,
        ok=False,
        code=code,
        message=message,
        state={
            "connection_state": "CONNECTED",
            "operating_mode": "MANUAL",
            "robot_state": "ERROR",
            "job_state": "REJECTED",
            "accept_state": "BLOCKED",
            "ui_mode": "READY",
        },
        perf={
            "elapsed_ms": 0,
            "mock": True,
        },
        err=[error_entry(code, message, f"mock_{robot_id}", detail)],
    )


def state_for_success(op: str) -> Dict[str, Any]:
    if op in STOP_OPS:
        robot_state = "STOPPED"
        job_state = "NONE"
        ui_mode = "READY"
    elif op in PAUSE_OPS:
        robot_state = "PAUSED"
        job_state = "PAUSED"
        ui_mode = "PAUSED"
    elif op in RESUME_OPS:
        robot_state = "IDLE"
        job_state = "NONE"
        ui_mode = "READY"
    elif op in {"start_mapping"}:
        robot_state = "MAPPING"
        job_state = "RUNNING"
        ui_mode = "BUSY_QUEUEABLE"
    elif op in {"nav_goal"}:
        robot_state = "NAVIGATING"
        job_state = "RUNNING"
        ui_mode = "BUSY_QUEUEABLE"
    elif op in MOVE_OPS:
        robot_state = "IDLE"
        job_state = "DONE"
        ui_mode = "READY"
    else:
        robot_state = "IDLE"
        job_state = "DONE"
        ui_mode = "READY"

    operating_mode = "MAPPING" if robot_state == "MAPPING" else "NAVIGATION" if robot_state == "NAVIGATING" else "MANUAL"
    return {
        "connection_state": "CONNECTED",
        "operating_mode": operating_mode,
        "robot_state": robot_state,
        "job_state": job_state,
        "accept_state": "ACCEPTING",
        "ui_mode": ui_mode,
    }


def result_code_for_op(op: str) -> str:
    if op in STOP_OPS:
        return "R_STOPPED"
    if op in PAUSE_OPS:
        return "R_PAUSED"
    if op in RESUME_OPS:
        return "R_RESUMED"
    if op in CANCEL_OPS:
        return "R_CANCELED"
    if op == "ping":
        return "R_PONG"
    if op == "save_map":
        return "R_MAP_LOCAL_SAVED"
    if op == "rsync_map":
        return "R_MAP_SYNCING"
    if op in STATUS_OPS:
        return "R_STATUS"
    return "R_DONE"


def handle_server_command_v4(command: Dict[str, Any], robot_id: str) -> Dict[str, Any]:
    valid, code, msg = validate_server_command_v4(command)
    if not valid:
        result = make_error_agent_result_v4(command, robot_id, "E_BAD_REQUEST", msg, {"validator_code": code})
        return result

    body = command_body_v4(command)
    command_robot_id = str(body.get("robot_id", ""))
    if command_robot_id != robot_id:
        return make_error_agent_result_v4(
            command,
            robot_id,
            "E_TARGET_INVALID",
            f"Mock agent controls {robot_id}, but command target is {command_robot_id}",
            {"command_robot_id": command_robot_id},
        )

    op = str(body.get("op", ""))
    params = body.get("params", {})
    if not isinstance(params, dict):
        params = {}

    if op not in MOVE_OPS and op not in STOP_OPS and op not in PAUSE_OPS and op not in RESUME_OPS and op not in CANCEL_OPS and op not in STATUS_OPS and op not in BACKGROUND_OPS:
        return make_error_agent_result_v4(command, robot_id, "E_UNKNOWN_ACTION", f"Unsupported op: {op}")

    start = time.monotonic()
    if op in STOP_OPS:
        time.sleep(0.02)
    elif op in MOVE_OPS:
        time.sleep(min(float(params.get("dur", 0.05) or 0.05), 0.05))
    else:
        time.sleep(0.01)

    elapsed_ms = int((time.monotonic() - start) * 1000)
    dur = float(params.get("dur", 0.0) or 0.0)
    hz = int(params.get("hz", 10) or 10)
    result = make_agent_result_v4(
        command,
        robot_id,
        ok=True,
        code=result_code_for_op(op),
        message=f"mock {robot_id} completed {op}",
        state=state_for_success(op),
        perf={
            "elapsed_ms": elapsed_ms,
            "mock": True,
            "dur": dur,
            "hz": hz,
            "pub": max(0, int(dur * hz)),
            "sent_cmd_vel_zero": op in STOP_OPS or bool(params.get("stop")),
        },
        err=[],
    )

    valid_result, result_code, result_msg = validate_agent_result_v4(result)
    if not valid_result:
        return make_error_agent_result_v4(
            command,
            robot_id,
            "E_INTERNAL_ERROR",
            f"mock generated invalid agent_result: {result_msg}",
            {"validator_code": result_code, "generated": result},
        )
    return result


def make_client_heartbeat_response_v5(request: Dict[str, Any], gateway_mode: bool, robot_id: str) -> Dict[str, Any]:
    requested = request.get("request", {})
    if not isinstance(requested, dict):
        requested = {}
    robots_requested = requested.get("robots", [])
    if not isinstance(robots_requested, list) or not robots_requested:
        robots_requested = sorted(KNOWN_ROBOTS) if gateway_mode else [robot_id]

    robots = {}
    for target in robots_requested:
        target_text = str(target)
        if target_text in KNOWN_ROBOTS or not gateway_mode:
            robots[target_text] = base_ready_state()

    response = make_common_message_v5(
        mt="client_heartbeat_response",
        source=str(request.get("dest", "robot_command_client")),
        dest="fleet_server",
        msg_id=make_msg_id("MSG", "client_heartbeat_response"),
    )
    response.update(
        {
            "ref": request.get("msg_id", ""),
            "ok": True,
            "code": "R_CLIENT_ALIVE",
            "message": "mock robot command client alive",
            "client": {
                "connection_state": "CONNECTED",
                "mock": True,
                "mode": "gateway" if gateway_mode else "per-robot",
            },
            "robots": robots,
        }
    )
    valid, code, msg = validate_client_heartbeat_response_v5(response)
    if not valid:
        response["ok"] = False
        response["code"] = "E_INTERNAL_ERROR"
        response["message"] = msg
        response["validator_code"] = code
    return response


def make_client_data_prepare_response_v5(request: Dict[str, Any], gateway_mode: bool, robot_id: str) -> Dict[str, Any]:
    requested = request.get("request", {})
    if not isinstance(requested, dict):
        requested = {}
    active_robot_id = str(requested.get("robot_id") or robot_id)
    if gateway_mode and active_robot_id not in KNOWN_ROBOTS:
        active_robot_id = "14"
    session_id = str(requested.get("session_id") or make_msg_id("MAPSYNC", active_robot_id))
    base_dir = Path("/tmp") / "turtlebot_mock_maps" / safe_mock_name(session_id)
    base_dir.mkdir(parents=True, exist_ok=True)
    image_path = base_dir / "tb1_latest_map.png"
    yaml_path = base_dir / "tb1_latest_map.yaml"
    image_path.write_bytes(MOCK_PNG_BYTES)
    yaml_path.write_text(
        "image: tb1_latest_map.png\nresolution: 0.05\norigin: [0.0, 0.0, 0.0]\nnegate: 0\noccupied_thresh: 0.65\nfree_thresh: 0.196\n",
        encoding="utf-8",
    )
    response = make_common_message_v5(
        mt="client_data_prepare_response",
        source=str(request.get("dest", "robot_command_client")),
        dest="fleet_server",
        msg_id=make_msg_id("MSG", "client_data_prepare_response"),
    )
    response.update(
        {
            "ref": request.get("msg_id", ""),
            "ok": True,
            "code": "R_MAP_READY",
            "message": "mock map files prepared",
            "robot_id": active_robot_id,
            "session_id": session_id,
            "transfer": {
                "method": "local_copy",
            },
            "files": [
                {
                    "kind": "map_image",
                    "name": image_path.name,
                    "local_path": str(image_path),
                    "bytes": image_path.stat().st_size,
                },
                {
                    "kind": "map_yaml",
                    "name": yaml_path.name,
                    "local_path": str(yaml_path),
                    "bytes": yaml_path.stat().st_size,
                },
            ],
        }
    )
    return response


def safe_mock_name(value: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in {".", "_", "-"} else "_" for ch in value)
    return safe.strip("._") or "session"


def handle_server_command_v5(command: Dict[str, Any], robot_id: str) -> Dict[str, Any]:
    valid, code, msg = validate_server_command_v5(command)
    if not valid:
        return make_error_agent_result_v5(command, robot_id, "E_BAD_REQUEST", msg, {"validator_code": code})

    body = command_body_v4(command)
    command_robot_id = str(body.get("robot_id", ""))
    if command_robot_id != robot_id:
        return make_error_agent_result_v5(
            command,
            robot_id,
            "E_TARGET_INVALID",
            f"Mock client controls {robot_id}, but command target is {command_robot_id}",
            {"command_robot_id": command_robot_id},
        )

    op = str(body.get("op", ""))
    params = body.get("params", {})
    if not isinstance(params, dict):
        params = {}

    if op not in MOVE_OPS and op not in STOP_OPS and op not in PAUSE_OPS and op not in RESUME_OPS and op not in CANCEL_OPS and op not in STATUS_OPS and op not in BACKGROUND_OPS:
        return make_error_agent_result_v5(command, robot_id, "E_UNKNOWN_ACTION", f"Unsupported op: {op}")

    start = time.monotonic()
    if op in STOP_OPS:
        time.sleep(0.02)
    elif op in MOVE_OPS:
        time.sleep(min(float(params.get("dur", 0.05) or 0.05), 0.05))
    else:
        time.sleep(0.01)

    dur = float(params.get("dur", 0.0) or 0.0)
    hz = int(params.get("hz", 10) or 10)
    result = make_agent_result_v5(
        command,
        robot_id,
        ok=True,
        code=result_code_for_op(op),
        message=f"mock {robot_id} completed {op}",
        state=state_for_success(op),
        perf={
            "elapsed_ms": int((time.monotonic() - start) * 1000),
            "mock": True,
            "dur": dur,
            "hz": hz,
            "pub": max(0, int(dur * hz)),
            "sent_cmd_vel_zero": op in STOP_OPS or bool(params.get("stop")),
        },
        err=[],
    )
    valid_result, result_code, result_msg = validate_agent_result_v5(result)
    if not valid_result:
        return make_error_agent_result_v5(
            command,
            robot_id,
            "E_INTERNAL_ERROR",
            f"mock generated invalid agent_result: {result_msg}",
            {"validator_code": result_code, "generated": result},
        )
    return result


def handle_connection(conn: socket.socket, addr: Tuple[str, int], robot_id: str) -> None:
    peer_ip, peer_port = addr
    gateway_mode = robot_id.startswith("gateway")
    try:
        with conn:
            file_obj = conn.makefile("r", encoding="utf-8")
            try:
                command = recv_json_line(file_obj)
            except ProtocolError as exc:
                command = make_common_message(
                    mt="server_command",
                    source="fleet_server",
                    dest=source_for_robot(robot_id),
                    msg_id="",
                )
                command["command"] = {
                    "command_id": "",
                    "command_revision": 0,
                    "op": "",
                    "server_priority": 99,
                    "blocking_type": "NONE",
                    "interrupt_policy": "status_only",
                    "robot_id": "tb3_1" if gateway_mode else robot_id,
                    "ros": {},
                    "params": {},
                    "timeout_sec": 0.0,
                }
                result = make_error_agent_result_v4(command, "tb3_1" if gateway_mode else robot_id, "E_BAD_REQUEST", str(exc))
                send_json(conn, result)
                return

            if command is None:
                return

            if command.get("v") == FLEET_JSON_VERSION_V5 and command.get("mt") == "client_data_prepare_request":
                print(
                    f"[{robot_id}] received v5 data prepare from {peer_ip}:{peer_port}: "
                    f"{command.get('msg_id')}"
                )
                response = make_client_data_prepare_response_v5(command, gateway_mode=gateway_mode, robot_id=robot_id)
                send_json(conn, response)
                print(f"[{robot_id}] sent v5 data prepare: {response.get('code')}")
                return

            if command.get("v") == FLEET_JSON_VERSION_V5 and command.get("mt") == "client_heartbeat_request":
                print(
                    f"[{robot_id}] received v5 heartbeat from {peer_ip}:{peer_port}: "
                    f"{command.get('msg_id')}"
                )
                response = make_client_heartbeat_response_v5(command, gateway_mode=gateway_mode, robot_id=robot_id)
                send_json(conn, response)
                print(f"[{robot_id}] sent v5 heartbeat: {response.get('code')}")
                return

            if command.get("v") == FLEET_JSON_VERSION_V5 and command.get("mt") == "server_command":
                body = command_body_v4(command)
                active_robot_id = str(body.get("robot_id", ""))
                if gateway_mode:
                    if active_robot_id not in KNOWN_ROBOTS:
                        result = make_error_agent_result_v5(
                            command,
                            "tb3_1",
                            "E_TARGET_INVALID",
                            f"Gateway mock does not know robot_id: {active_robot_id}",
                            {"robot_id": active_robot_id, "known_robots": sorted(KNOWN_ROBOTS)},
                        )
                        send_json(conn, result)
                        return
                else:
                    active_robot_id = robot_id
                print(
                    f"[{robot_id}] received v5 command from {peer_ip}:{peer_port}: "
                    f"{command.get('msg_id')} {body.get('command_id')} {body.get('op')}"
                )
                result = handle_server_command_v5(command, active_robot_id)
                send_json(conn, result)
                print(f"[{robot_id}] sent v5 result: {result.get('code')}")
                return

            if command.get("v") == FLEET_JSON_VERSION and command.get("mt") == "heartbeat_request":
                active_robot_id = str(command.get("robot_id", ""))
                if gateway_mode:
                    if active_robot_id not in KNOWN_ROBOTS:
                        active_robot_id = "tb3_1"
                else:
                    active_robot_id = robot_id
                print(
                    f"[{robot_id}] received heartbeat from {peer_ip}:{peer_port}: "
                    f"{command.get('msg_id')} target={command.get('robot_id')}"
                )
                response, state_report = handle_heartbeat_request_v4(command, active_robot_id)
                send_json(conn, response)
                if state_report is not None:
                    send_json(conn, state_report)
                print(
                    f"[{robot_id}] sent heartbeat: {response.get('code', '')} "
                    f"state_report={state_report is not None}"
                )
                return

            if command.get("v") == FLEET_JSON_VERSION and command.get("mt") == "server_command":
                body = command_body_v4(command)
                active_robot_id = str(body.get("robot_id", ""))
                if gateway_mode:
                    if active_robot_id not in KNOWN_ROBOTS:
                        result = make_error_agent_result_v4(
                            command,
                            "tb3_1",
                            "E_TARGET_INVALID",
                            f"Gateway mock does not know robot_id: {active_robot_id}",
                            {"robot_id": active_robot_id, "known_robots": sorted(KNOWN_ROBOTS)},
                        )
                        send_json(conn, result)
                        return
                else:
                    active_robot_id = robot_id
                print(
                    f"[{robot_id}] received v4 from {peer_ip}:{peer_port}: "
                    f"{command.get('msg_id')} {body.get('command_id')} {body.get('op')}"
                )
                result = handle_server_command_v4(command, active_robot_id)
                send_json(conn, result)
                print(f"[{robot_id}] sent v4 result: {result.get('code')}")
                return

            if gateway_mode:
                robot_id = str(command.get("to") or "tb3_1")
            print(f"[{robot_id}] received legacy from {peer_ip}:{peer_port}: {command.get('id')} {command.get('op')}")

            valid, code, msg = validate_json_command_v03(command)
            if not valid:
                result = make_legacy_result(
                    command,
                    robot_id,
                    ok=False,
                    st="rejected",
                    code=code,
                    err=[error_entry(code, msg, f"mock_{robot_id}")],
                )
                send_json(conn, result)
                return

            if command.get("to") != robot_id:
                result = make_legacy_result(
                    command,
                    robot_id,
                    ok=False,
                    st="rejected",
                    code="E_INVALID_TARGET",
                    err=[
                        error_entry(
                            "E_INVALID_TARGET",
                            f"Mock agent controls {robot_id}, but command target is {command.get('to')}",
                            f"mock_{robot_id}",
                        )
                    ],
                )
                send_json(conn, result)
                return

            op = command.get("op")
            if op == "move_vel":
                time.sleep(0.05)
                result = make_legacy_result(command, robot_id, ok=True, st="done", code="R_OK", err=[])
            elif op == "stop":
                time.sleep(0.02)
                result = make_legacy_result(command, robot_id, ok=True, st="stopped", code="R_STOPPED", err=[])
            elif op == "ping":
                result = make_legacy_result(command, robot_id, ok=True, st="done", code="R_PONG", err=[])
            else:
                result = make_legacy_result(
                    command,
                    robot_id,
                    ok=False,
                    st="rejected",
                    code="E_UNSUPPORTED_OP",
                    err=[error_entry("E_UNSUPPORTED_OP", f"Unsupported op: {op}", f"mock_{robot_id}")],
                )

            send_json(conn, result)
            print(f"[{robot_id}] sent result: {result.get('code')}")
    except OSError as exc:
        print(f"[{robot_id}] connection error: {exc}")


def serve_agent(robot_id: str, bind_ip: str, port: int) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((bind_ip, int(port)))
    sock.listen(20)
    print(f"[{robot_id}] mock agent listening on {bind_ip}:{port}")

    try:
        while True:
            conn, addr = sock.accept()
            thread = threading.Thread(target=handle_connection, args=(conn, addr, robot_id), daemon=True)
            thread.start()
    except KeyboardInterrupt:
        print(f"\n[{robot_id}] mock agent stopped.")
    finally:
        sock.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mock robot agent for communication test")
    parser.add_argument("--bind-ip", default="127.0.0.1")
    parser.add_argument("--mode", choices=["gateway", "per-robot"], default="gateway")
    parser.add_argument("--robot", choices=["all", "tb3_1", "tb3_2", "tb3_3"], default="all")
    parser.add_argument("--port", type=int, default=0, help="Single-port mock listen port")
    parser.add_argument("--multi-port", action="store_true", help="Listen on health, command, and data-control ports")
    parser.add_argument("--health-port", type=int, default=DEFAULT_GATEWAY_PORT)
    parser.add_argument("--command-port", type=int, default=DEFAULT_COMMAND_PORT)
    parser.add_argument("--data-control-port", type=int, default=DEFAULT_DATA_CONTROL_PORT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.mode == "gateway":
        if args.multi_port:
            ports = [
                ("health", args.health_port),
                ("command", args.command_port),
                ("data_control", args.data_control_port),
            ]
            threads = []
            for label, port in ports:
                thread = threading.Thread(target=serve_agent, args=(f"gateway_{label}", args.bind_ip, port), daemon=True)
                thread.start()
                threads.append(thread)
            print("Mock gateway multi-port listeners are running. Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(1.0)
            except KeyboardInterrupt:
                print("\nMock gateway multi-port listeners stopped.")
            return
        port = args.port or DEFAULT_GATEWAY_PORT
        serve_agent("gateway", args.bind_ip, port)
        return

    if args.robot == "all":
        raise SystemExit(
            "v0.5 uses Robot Command Client gateway ports 5000/5001/5002. "
            "Use --mode gateway --multi-port, or choose one --robot with a custom --port."
        )
        return

    port = args.port or DEFAULT_GATEWAY_PORT
    serve_agent(args.robot, args.bind_ip, port)


if __name__ == "__main__":
    main()
