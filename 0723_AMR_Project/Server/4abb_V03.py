# Server_4abb_V3.py
#
# 4abb 로봇 옆 노트북에서 실행하는 중계기 프로그램 (V3).
# 설정값이 이 파일 안에 이미 채워져 있으므로, 별도 설정 파일 없이 이 파일 하나만
# 그대로 실행하면 됩니다.
#
# V3에서 바뀐 것: ABB_HOST가 3abb/5abb와 똑같이 "192.168.3.3"으로 복사되어
# 있었던 게 버그였음 - 4abb는 desktop-mcn21av(담당자 PC)에서 도는 컨트롤러라
# 실제로는 그 PC의 Tailscale 주소를 써야 연결이 됨. 이제 그 주소로 고침.
#
# V1과의 차이 (A안): V1은 ABB나 관리자 서버 중 하나라도 아직 안 켜져 있으면
# 첫 접속에서 바로 포기하고 프로그램이 끝나버려서, 반드시 "관리자 서버 →
# ABB Main() → 이 커넥터" 순서로 켜야만 했다. V2는 첫 접속도 무한 재시도하므로
# 셋 중 무엇을 먼저 켜도 상관없다 - 아직 안 켜진 쪽은 이 스크립트가 알아서
# 기다렸다가 뜨는 즉시 연결한다.
#
# 역할이 두 가지지만 순차적으로 처리함(스레드 불필요):
#   1) ABB 로봇(TestServer.mod)에 클라이언트로 접속
#   2) 총괄 관리자 서버(TestServer_admin.py)에 클라이언트로 접속
# 이후로는 "관리자에게서 명령을 받으면 그 즉시 같은 명령을 ABB로 그대로 전달"만
# 반복하는 단순 중계 루프. ABB는 별도 응답을 보내지 않으므로(TestServer.mod 참고)
# 이 스크립트도 ABB로부터 뭔가를 읽어오지 않음.

import socket
import time


RELAY_NAME = "4abb"

ABB_HOST = "100.102.179.115"   # desktop-mcn21av (4abb 담당자) Tailscale IP
ABB_PORT = 5000

ADMIN_HOST = "100.109.178.123"   # desktop-12mccaq (서버장) Tailscale IP
ADMIN_PORT = 5000

ENCODING = "utf-8"
QUIT_MESSAGE = "/quit"
RECONNECT_DELAY_SECONDS = 2


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
    """접속을 한 번 시도하고, 실패하면 안내 메시지를 출력한 뒤 None을 반환."""
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


def connect_with_retry(host, port, label):
    """연결될 때까지 반복 시도 (실패하면 잠깐 대기 후 재시도).

    ABB Main(), 관리자 서버, 이 커넥터를 어떤 순서로 켜도 상관없게 해주는
    부분 - 상대가 아직 안 켜져 있으면 이 함수가 뜰 때까지 기다린다."""
    while True:
        connection = connect_as_client(host, port, label)
        if connection is not None:
            return connection
        time.sleep(RECONNECT_DELAY_SECONDS)


def run_connector(abb_host, abb_port, admin_host, admin_port, relay_name):
    """ABB, 관리자 순서로 접속한 뒤 관리자 명령을 그대로 ABB로 전달.

    두 접속 모두 상대가 아직 준비되지 않았으면 뜰 때까지 재시도하며 기다린다
    (connect_with_retry).

    ABB와의 연결만 끊기면 관리자와의 연결은 그대로 둔 채 ABB 쪽만 재연결을
    시도한다 - 관리자 쪽에서 보면 이 중계기는 계속 접속된 상태로 남아있는다."""
    abb_connection = connect_with_retry(abb_host, abb_port, "ABB 로봇")
    admin_connection = connect_with_retry(admin_host, admin_port, "관리자 서버")

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
                abb_connection = connect_with_retry(abb_host, abb_port, "ABB 로봇")
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
    print(f"[{RELAY_NAME}] 중계기 프로그램을 시작합니다.")

    try:
        run_connector(ABB_HOST, ABB_PORT, ADMIN_HOST, ADMIN_PORT, RELAY_NAME)
    except KeyboardInterrupt:
        print()
        print("중계기를 종료합니다.")
