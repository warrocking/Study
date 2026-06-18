import socket
import json
import time
from datetime import datetime
from pathlib import Path

import rclpy
from geometry_msgs.msg import Twist


# =========================
# 기본 설정
# =========================

DEFAULT_SERVER_IP = "192.168.0.78"
DEFAULT_PORT = 5000

CONFIG_FILE = Path("client_move_config.json")
LOG_DIR = Path("logs/client_move")


# =========================
# 공통 함수
# =========================

def now_ts():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def safe_time_string():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def load_config():
    if not CONFIG_FILE.exists():
        return {}

    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(config):
    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def save_json_log(prefix, data):
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    time_text = safe_time_string()

    history_path = LOG_DIR / f"{prefix}_{time_text}.json"
    latest_path = LOG_DIR / f"latest_{prefix}.json"

    with history_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with latest_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[저장] {history_path}")
    print(f"[저장] {latest_path}")


def ask_value(config, key, default_value, message):
    current_value = config.get(key, default_value)
    user_input = input(f"{message} [{current_value}] : ").strip()

    if user_input == "":
        return current_value

    config[key] = user_input
    save_config(config)
    return user_input


def ask_int(config, key, default_value, message):
    current_value = config.get(key, default_value)
    user_input = input(f"{message} [{current_value}] : ").strip()

    if user_input == "":
        return int(current_value)

    value = int(user_input)
    config[key] = value
    save_config(config)
    return value


def send_json(sock, data):
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    sock.sendall((text + "\n").encode("utf-8"))


def recv_json(file_obj):
    line = file_obj.readline()

    if line == "":
        return None

    return json.loads(line)


def make_stop_twist():
    msg = Twist()
    msg.linear.x = 0.0
    msg.linear.y = 0.0
    msg.linear.z = 0.0
    msg.angular.x = 0.0
    msg.angular.y = 0.0
    msg.angular.z = 0.0
    return msg


def make_move_twist(linear_x, angular_z):
    msg = Twist()
    msg.linear.x = float(linear_x)
    msg.angular.z = float(angular_z)
    return msg


def execute_cmd_vel(node, topic, linear_x, angular_z, duration_sec, rate_hz, stop_after):
    """
    json_command의 cmd.p 값을 ROS2 /cmd_vel Twist 메시지로 변환해서 발행한다.
    """
    publisher = node.create_publisher(Twist, topic, 10)

    move_msg = make_move_twist(linear_x, angular_z)
    stop_msg = make_stop_twist()

    period = 1.0 / float(rate_hz)
    start_time = time.time()
    count = 0

    print()
    print("[ROS2 실행] cmd_vel 발행 시작")
    print(f"topic = {topic}")
    print(f"linear_x = {linear_x}")
    print(f"angular_z = {angular_z}")
    print(f"duration_sec = {duration_sec}")
    print(f"rate_hz = {rate_hz}")
    print()

    while time.time() - start_time < float(duration_sec):
        publisher.publish(move_msg)
        rclpy.spin_once(node, timeout_sec=0.0)
        count += 1
        time.sleep(period)

    if stop_after:
        print("[ROS2 실행] 정지 명령 발행")
        for _ in range(10):
            publisher.publish(stop_msg)
            rclpy.spin_once(node, timeout_sec=0.0)
            time.sleep(0.05)

    print("[ROS2 실행] cmd_vel 발행 완료")
    return count


def make_json_result(json_command, ok, state, code, err_list, publish_count, start_ts, end_ts):
    job = json_command.get("job", {})
    cmd = json_command.get("cmd", {})
    tgt = json_command.get("tgt", {})
    p = cmd.get("p", {})

    duration_sec = float(p.get("duration_sec", 0.0))
    linear_x = float(p.get("linear_x", 0.0))

    return {
        "ver": "1.0",
        "mt": "job_result",
        "mid": f"M{safe_time_string()}_0020",
        "ts": now_ts(),
        "src": "robot_gateway",
        "dst": "server_hmi",

        "job": {
            "jid": job.get("jid", ""),
            "name": job.get("name", ""),
            "req_ts": json_command.get("ts", ""),
            "start_ts": start_ts,
            "end_ts": end_ts
        },

        "cmd": {
            "cid": cmd.get("cid", ""),
            "type": cmd.get("type", "")
        },

        "tgt": {
            "rid": tgt.get("rid", ""),
            "rname": tgt.get("rname", ""),
            "ns": tgt.get("ns", "")
        },

        "rs": {
            "state": state,
            "ok": ok,
            "code": code
        },

        "pre": {
            "bat": {
                "v": None,
                "pct": None,
                "st": "not_checked"
            },
            "cam": {
                "conn": None,
                "st": "not_checked"
            },
            "pos": {
                "x": None,
                "y": None,
                "th": None
            }
        },

        "perf": {
            "dist": abs(linear_x) * duration_sec,
            "dur": duration_sec,
            "move_t": duration_sec,
            "pause_t": 0,
            "avg_v": abs(linear_x),
            "max_v": abs(linear_x),
            "publish_n": publish_count,
            "pause_n": 0,
            "estop_n": 0,
            "offline_n": 0
        },

        "post": {
            "bat": {
                "v": None,
                "pct": None,
                "st": "not_checked"
            },
            "cam": {
                "conn": None,
                "st": "not_checked"
            },
            "pos": {
                "x": None,
                "y": None,
                "th": None
            }
        },

        "err": err_list
    }


def validate_json_command(json_command):
    if json_command.get("mt") != "job_cmd":
        return False, "E_INVALID_MESSAGE_TYPE", "mt가 job_cmd가 아닙니다."

    cmd = json_command.get("cmd", {})
    p = cmd.get("p", {})

    if cmd.get("type") != "move_velocity":
        return False, "E_INVALID_COMMAND_TYPE", "cmd.type이 move_velocity가 아닙니다."

    if cmd.get("ros") != "topic":
        return False, "E_INVALID_ROS_MODE", "cmd.ros가 topic이 아닙니다."

    required = ["topic", "linear_x", "angular_z", "duration_sec", "rate_hz", "stop_after"]

    for key in required:
        if key not in p:
            return False, "E_MISSING_PARAMETER", f"cmd.p.{key} 값이 없습니다."

    return True, "", ""


# =========================
# 클라이언트 메인
# =========================

def main():
    config = load_config()

    print("====================================")
    print(" JSON CLIENT MOVE TB1")
    print(" 클라이언트 역할: json_command 수신 → ROS2 cmd_vel 실행 → json_result 전송")
    print("====================================")
    print()

    server_ip = ask_value(
        config,
        "server_ip",
        DEFAULT_SERVER_IP,
        "접속할 서버 IP를 입력하세요. 공백이면 기본값 사용"
    )

    port = ask_int(
        config,
        "port",
        DEFAULT_PORT,
        "접속할 포트 번호를 입력하세요. 공백이면 기본값 사용"
    )

    print()
    print(f"[설정] server_ip = {server_ip}")
    print(f"[설정] port = {port}")
    print()

    rclpy.init()
    node = rclpy.create_node("json_client_move_tb1")

    try:
        while True:
            try:
                print(f"[접속 시도] {server_ip}:{port}")

                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_sock:
                    client_sock.connect((server_ip, port))

                    print("[접속 성공] 서버에 연결되었습니다.")
                    print()

                    file_obj = client_sock.makefile("r", encoding="utf-8")

                    print("[대기] 서버의 json_command 수신 대기...")

                    json_command = recv_json(file_obj)

                    if json_command is None:
                        print("[오류] 서버가 연결을 종료했습니다.")
                        return

                    print()
                    print("[수신] json_command")
                    print(json.dumps(json_command, ensure_ascii=False, indent=2))

                    save_json_log("json_command_received", json_command)

                    valid, err_code, err_msg = validate_json_command(json_command)

                    start_ts = now_ts()
                    publish_count = 0
                    err_list = []

                    if valid:
                        cmd = json_command.get("cmd", {})
                        p = cmd.get("p", {})

                        topic = p.get("topic")
                        linear_x = p.get("linear_x")
                        angular_z = p.get("angular_z")
                        duration_sec = p.get("duration_sec")
                        rate_hz = p.get("rate_hz")
                        stop_after = p.get("stop_after")

                        try:
                            publish_count = execute_cmd_vel(
                                node=node,
                                topic=topic,
                                linear_x=linear_x,
                                angular_z=angular_z,
                                duration_sec=duration_sec,
                                rate_hz=rate_hz,
                                stop_after=stop_after
                            )

                            end_ts = now_ts()
                            json_result = make_json_result(
                                json_command=json_command,
                                ok=True,
                                state="completed",
                                code="R_OK",
                                err_list=[],
                                publish_count=publish_count,
                                start_ts=start_ts,
                                end_ts=end_ts
                            )

                        except Exception as e:
                            end_ts = now_ts()
                            err_list = [
                                {
                                    "eid": "E0001",
                                    "lv": "error",
                                    "type": "ros2_publish_error",
                                    "code": "E_ROS2_PUBLISH_ERROR",
                                    "msg": str(e),
                                    "src": "json_client_move_tb1",
                                    "det_ts": now_ts(),
                                    "clr_ts": None,
                                    "act": "stop_or_no_action",
                                    "resolved": False
                                }
                            ]

                            json_result = make_json_result(
                                json_command=json_command,
                                ok=False,
                                state="failed",
                                code="R_ROS2_PUBLISH_ERROR",
                                err_list=err_list,
                                publish_count=publish_count,
                                start_ts=start_ts,
                                end_ts=end_ts
                            )

                    else:
                        end_ts = now_ts()
                        err_list = [
                            {
                                "eid": "E0001",
                                "lv": "error",
                                "type": "invalid_json_command",
                                "code": err_code,
                                "msg": err_msg,
                                "src": "json_client_move_tb1",
                                "det_ts": now_ts(),
                                "clr_ts": None,
                                "act": "reject_job",
                                "resolved": False
                            }
                        ]

                        json_result = make_json_result(
                            json_command=json_command,
                            ok=False,
                            state="failed",
                            code="R_INVALID_JSON_COMMAND",
                            err_list=err_list,
                            publish_count=0,
                            start_ts=start_ts,
                            end_ts=end_ts
                        )

                    print()
                    print("[송신] json_result")
                    print(json.dumps(json_result, ensure_ascii=False, indent=2))

                    send_json(client_sock, json_result)
                    save_json_log("json_result_sent", json_result)

                    print()
                    print("[완료] 서버 → 클라이언트 → TurtleBot 1 이동 테스트 완료")
                    return

            except ConnectionRefusedError:
                print("[대기] 서버가 아직 열려 있지 않습니다. 3초 후 재시도합니다.")
                time.sleep(3)

            except TimeoutError:
                print("[대기] 연결 시간이 초과되었습니다. 3초 후 재시도합니다.")
                time.sleep(3)

            except OSError as e:
                print(f"[오류] 연결 실패: {e}")
                print("[대기] 3초 후 재시도합니다.")
                time.sleep(3)

            except KeyboardInterrupt:
                print()
                print("[종료] 클라이언트를 종료합니다.")
                return

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
