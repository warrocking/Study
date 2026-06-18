
import socket
import json
from datetime import datetime
from pathlib import Path


# =========================
# 기본 설정
# =========================

DEFAULT_SERVER_IP = "192.168.0.78"
DEFAULT_CLIENT_IP = "192.168.0.137"
DEFAULT_PORT = 5000

CONFIG_FILE = Path("server_config.json")
LOG_DIR = Path("logs/server")


# =========================
# 공통 함수
# =========================

def now_ts():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def safe_time_string():
    """
    파일 이름에 사용할 수 있는 시간 문자열을 만든다.
    예: 20260616_182531
    """
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
    """
    JSON 데이터를 logs/server 폴더에 저장한다.

    prefix 예:
    - json_command_sent
    - json_result_received
    """
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
    """
    JSON 객체를 한 줄 문자열로 변환해서 전송한다.
    끝에 \\n을 붙여서 수신 측에서 한 메시지의 끝을 알 수 있게 한다.
    """
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    sock.sendall((text + "\n").encode("utf-8"))


def recv_json(file_obj):
    """
    한 줄을 읽어서 JSON 객체로 변환한다.
    """
    line = file_obj.readline()

    if line == "":
        return None

    return json.loads(line)


def make_json_command():
    """
    서버 → 클라이언트로 보내는 테스트용 json_command.
    나중에는 HMI 버튼 입력값으로 이 내용을 만들면 된다.
    """
    return {
        "ver": "1.0",
        "mt": "job_cmd",
        "mid": "M20260616_0001",
        "ts": now_ts(),
        "src": "server_hmi",
        "dst": "robot_gateway",

        "job": {
            "jid": "J0001",
            "name": "tb3_1_move_to_point",
            "prio": "normal"
        },

        "tgt": {
            "rid": "tb3_1",
            "rname": "TurtleBot 1",
            "ns": "/tb3_1"
        },

        "cmd": {
            "cid": "C0001",
            "type": "move_to",
            "ros": "nav2_action",
            "p": {
                "x": 2.0,
                "y": 1.5,
                "th": 0.0,
                "vmax": 0.15,
                "wmax": 0.5,
                "pos_tol": 0.1,
                "ang_tol": 0.1,
                "max_t": 60
            }
        },

        "pol": {
            "offline_run": True,
            "save_progress": True,
            "resume_by_operator": True,
            "stop_person": True,
            "stop_cam_err": True,
            "stop_robot_lost": True,
            "stop_timeout": True,
            "min_bat_pct": 30,
            "min_bat_v": 11.0
        },

        "rpt": {
            "need_pre": True,
            "need_post": True,
            "need_perf": True,
            "need_err": True
        }
    }


# =========================
# 서버 메인
# =========================

def main():
    config = load_config()

    print("====================================")
    print(" JSON SERVER")
    print(" 서버 역할: json_command 전송 / json_result 수신")
    print("====================================")
    print()

    server_ip = ask_value(
        config,
        "server_ip",
        DEFAULT_SERVER_IP,
        "서버가 열 IP를 입력하세요. 공백이면 기본값 사용"
    )

    allowed_client_ip = ask_value(
        config,
        "allowed_client_ip",
        DEFAULT_CLIENT_IP,
        "예상 클라이언트 IP를 입력하세요. 공백이면 기본값 사용"
    )

    port = ask_int(
        config,
        "port",
        DEFAULT_PORT,
        "사용할 포트 번호를 입력하세요. 공백이면 기본값 사용"
    )

    print()
    print(f"[설정] server_ip = {server_ip}")
    print(f"[설정] allowed_client_ip = {allowed_client_ip}")
    print(f"[설정] port = {port}")
    print()

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_sock.bind((server_ip, port))
    except OSError as e:
        print("[경고] 지정한 IP로 bind 실패:", e)
        print("[대체] 0.0.0.0 으로 모든 네트워크 인터페이스에서 대기합니다.")
        server_sock.bind(("0.0.0.0", port))

    server_sock.listen(1)

    print(f"[대기] 클라이언트 접속 대기 중... port={port}")
    print("종료하려면 Ctrl + C")
    print()

    try:
        while True:
            conn, addr = server_sock.accept()
            client_ip, client_port = addr

            print("====================================")
            print(f"[접속] 클라이언트 접속됨: {client_ip}:{client_port}")

            if client_ip != allowed_client_ip:
                print(f"[주의] 예상 클라이언트 IP({allowed_client_ip})와 실제 접속 IP({client_ip})가 다릅니다.")
                print("[처리] 테스트 목적이므로 접속은 허용합니다.")

            with conn:
                file_obj = conn.makefile("r", encoding="utf-8")

                json_command = make_json_command()

                print()
                print("[송신] json_command")
                print(json.dumps(json_command, ensure_ascii=False, indent=2))

                send_json(conn, json_command)
                save_json_log("json_command_sent", json_command)

                print()
                print("[대기] 클라이언트의 json_result 수신 대기...")

                json_result = recv_json(file_obj)

                if json_result is None:
                    print("[오류] 클라이언트가 연결을 종료했습니다.")
                    continue

                print()
                print("[수신] json_result")
                print(json.dumps(json_result, ensure_ascii=False, indent=2))

                save_json_log("json_result_received", json_result)

                print()
                print("[완료] JSON 송수신 테스트 성공")
                print("====================================")
                print()

    except KeyboardInterrupt:
        print()
        print("[종료] 서버를 종료합니다.")

    finally:
        server_sock.close()


if __name__ == "__main__":
    main()
PY
