# TestServer_Connector.py
#
# 중계기(옆 노트북)에서 실행하는 테스트 클라이언트.
# 이 파일은 새 버전이 나오면 통째로 덮어써도 되는 파일입니다 - 로봇/관리자 주소는
# 이 파일 안이 아니라 같은 폴더의 connector_config.txt에 있습니다. 그 설정 파일만
# 처음에 한 번 이 중계기가 담당하는 로봇/관리자 주소로 채워두면, 이 스크립트는
# 그 뒤로 다시 손댈 필요가 없습니다.
#
# 역할이 두 가지지만 순차적으로 처리함(스레드 불필요):
#   1) ABB 로봇(TestServer.mod)에 클라이언트로 접속
#   2) 총괄 관리자 서버(TestServer_admin.py)에 클라이언트로 접속
# 이후로는 "관리자에게서 명령을 받으면 그 즉시 같은 명령을 ABB로 그대로 전달"만
# 반복하는 단순 중계 루프. ABB는 별도 응답을 보내지 않으므로(TestServer.mod 참고)
# 이 스크립트도 ABB로부터 뭔가를 읽어오지 않음.

import socket
import time


CONFIG_PATH = "connector_config.txt"
ENCODING = "utf-8"
QUIT_MESSAGE = "/quit"
RECONNECT_DELAY_SECONDS = 2


def load_config(path):
    """KEY=VALUE 형식의 텍스트 파일을 읽어서 dict로 반환."""
    config = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()
    return config


def send_text(connection, text):
    connection.sendall((text + "\n").encode(ENCODING))


def receive_line(connection, buffer, timeout_seconds=1.0):
    """관리자 연결에서 한 줄(개행까지)을 읽는다 - 짧은 타임아웃을 계속 반복해서
    기다리기 때문에, 명령이 하나도 안 와도 주기적으로 파이썬 인터프리터로
    제어가 돌아온다. 타임아웃 없이 통짜로 블로킹해서 기다리면 Windows에서
    Ctrl+C(KeyboardInterrupt)가 그 blocking recv가 끝날 때까지 전달이
    미뤄지는 경우가 있어서, 명령이 없을 때 Ctrl+C가 안 먹히는 원인이었다.
    buffer는 이전 호출에서 개행 뒤에 남은 바이트를 다음 호출로 넘기기
    위한 값으로, 호출할 때마다 반환값으로 갱신해서 다시 넘겨야 한다.

    반환값: (line 또는 연결이 끊겼으면 None, 다음 호출에 넘길 buffer)."""
    connection.settimeout(timeout_seconds)
    while b"\n" not in buffer:
        try:
            chunk = connection.recv(4096)
        except socket.timeout:
            continue
        if not chunk:
            return None, buffer
        buffer += chunk

    line, _, rest = buffer.partition(b"\n")
    return line.decode(ENCODING).rstrip("\r"), rest


def connect_as_client(host, port, label):
    """접속을 시도하고, 실패하면 안내 메시지를 출력한 뒤 None을 반환."""
    print(f"{label}에 접속합니다: {host}:{port}")
    try:
        connection = socket.create_connection((host, port), timeout=10)
    except ConnectionRefusedError:
        print(f"{label}가 연결을 거부했습니다. 상대 프로그램이 실행 중인지 확인하세요.")
        return None
    except OSError as error:
        print(f"{label} 연결 오류:", error)
        return None

    connection.settimeout(None)   # 연결 후에는 타임아웃 없이 계속 대기 가능하게 해제
    print(f"[{label}에 연결되었습니다.]")
    return connection


def reconnect_to_abb(abb_host, abb_port):
    """ABB에 다시 연결될 때까지 반복 시도 (실패하면 잠깐 대기 후 재시도)."""
    while True:
        connection = connect_as_client(abb_host, abb_port, "ABB 로봇")
        if connection is not None:
            return connection
        time.sleep(RECONNECT_DELAY_SECONDS)


def run_connector(abb_host, abb_port, admin_host, admin_port, relay_name):
    """ABB, 관리자 순서로 접속한 뒤 관리자 명령을 그대로 ABB로 전달.

    ABB와의 연결만 끊기면 관리자와의 연결은 그대로 둔 채 ABB 쪽만 재연결을
    시도한다 - 관리자 쪽에서 보면 이 중계기는 계속 접속된 상태로 남아있는다."""
    abb_connection = connect_as_client(abb_host, abb_port, "ABB 로봇")
    if abb_connection is None:
        return

    admin_connection = connect_as_client(admin_host, admin_port, "관리자 서버")
    if admin_connection is None:
        abb_connection.close()
        return

    send_text(admin_connection, relay_name)   # 관리자에게 내 이름을 먼저 알림
    print(f"[관리자에게 이름을 알렸습니다: {relay_name}]")

    print("이제부터 관리자 명령을 그대로 ABB로 전달합니다.")
    admin_buffer = b""

    try:
        while True:
            command, admin_buffer = receive_line(admin_connection, admin_buffer)

            if command is None:
                print("[관리자 서버와의 연결이 종료되었습니다.]")
                break

            print(f"[관리자] {command}")

            try:
                send_text(abb_connection, command)
                print(f"[ABB로 전달함] {command}")
            except OSError as error:
                print(f"[ABB 연결이 끊겼습니다: {error}]")
                abb_connection.close()

                send_text(admin_connection, "ABB disconnected - reconnecting")
                abb_connection = reconnect_to_abb(abb_host, abb_port)
                send_text(admin_connection, "ABB reconnected")

                send_text(abb_connection, command)   # 실패했던 명령을 재접속 후 다시 전달
                print(f"[ABB로 전달함(재접속 후)] {command}")

            if command == QUIT_MESSAGE:
                print("[중계기를 종료합니다.]")
                break

    except OSError as error:
        print()
        print("중계 중 연결 오류:", error)

    finally:
        admin_connection.close()
        abb_connection.close()


if __name__ == "__main__":
    print("중계기 프로그램을 시작합니다.")

    try:
        config = load_config(CONFIG_PATH)
    except FileNotFoundError:
        print(f"설정 파일을 찾을 수 없습니다: {CONFIG_PATH}")
        print("같은 폴더에 connector_config.txt를 만들고 ABB_HOST/ABB_PORT/ADMIN_HOST/ADMIN_PORT 값을 채워주세요.")
        raise SystemExit(1)

    try:
        relay_name = config["RELAY_NAME"]
        abb_host = config["ABB_HOST"]
        abb_port = int(config["ABB_PORT"])
        admin_host = config["ADMIN_HOST"]
        admin_port = int(config["ADMIN_PORT"])
    except KeyError as missing:
        print(f"connector_config.txt에 {missing} 값이 없습니다.")
        raise SystemExit(1)

    try:
        run_connector(abb_host, abb_port, admin_host, admin_port, relay_name)
    except KeyboardInterrupt:
        print()
        print("중계기를 종료합니다.")
