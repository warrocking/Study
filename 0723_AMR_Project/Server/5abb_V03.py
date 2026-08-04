# Server_5abb_v3.py
#
# 5abb 로봇 옆 노트북에서 실행하는 중계기 프로그램 (V3 - 터미널 UI 테스트용).
# 설정값이 이 파일 안에 이미 채워져 있으므로, 별도 설정 파일 없이 이 파일 하나만
# 그대로 실행하면 됩니다.
#
# V2와의 차이: 동작 로직(첫 접속도 무한 재시도)은 V2와 동일하고, 터미널에
# 지금 무슨 상황인지 한눈에 보이도록 출력만 다시 꾸몄다.
#   - ABB / 관리자 서버 접속 상태를 항상 2줄로 같이 보여줌 (색상 + 아이콘)
#   - 재시도할 때마다 몇 번째 시도인지 숫자로 표시
#   - 명령 중계 로그에 시간/화살표를 붙여서 흐름이 잘 보이게 함
#
# 역할이 두 가지지만 순차적으로 처리함(스레드 불필요):
#   1) ABB 로봇(TestServer.mod)에 클라이언트로 접속
#   2) 총괄 관리자 서버(TestServer_admin.py)에 클라이언트로 접속
# 이후로는 "관리자에게서 명령을 받으면 그 즉시 같은 명령을 ABB로 그대로 전달"만
# 반복하는 단순 중계 루프. ABB는 별도 응답을 보내지 않으므로(TestServer.mod 참고)
# 이 스크립트도 ABB로부터 뭔가를 읽어오지 않음.

import socket
import sys
import time
from datetime import datetime

# Windows 콘솔의 기본 코드페이지(cp949 등)는 여기서 쓰는 박스 문자/이모지를
# 표현하지 못해 UnicodeEncodeError로 죽을 수 있다 (VSCode 통합 터미널은
# 보통 UTF-8이라 괜찮지만, cmd.exe 등 다른 콘솔에서 실행하면 발생). 실행 콘솔에
# 상관없이 항상 UTF-8로 출력하도록 강제해서 이 문제를 원천 차단한다.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


RELAY_NAME = "5abb"

ABB_HOST = "192.168.3.3"
ABB_PORT = 5000

ADMIN_HOST = "100.109.178.123"   # desktop-12mccaq (서버장) Tailscale IP
ADMIN_PORT = 5000

ENCODING = "utf-8"
QUIT_MESSAGE = "/quit"
RECONNECT_DELAY_SECONDS = 2


class C:
    """터미널 ANSI 색상 코드 - VSCode 통합 터미널, Windows Terminal, 최신
    PowerShell에서 기본 지원됨."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"


def now():
    return datetime.now().strftime("%H:%M:%S")


def print_banner():
    print(f"{C.BOLD}{C.CYAN}")
    print("═══════════════════════════════════════")
    print(f"   {RELAY_NAME} 중계기 프로그램을 시작합니다")
    print("═══════════════════════════════════════")
    print(C.RESET)


class StatusBoard:
    """ABB / 관리자 서버 접속 상태를 항상 2줄로 같이 보여준다.

    둘 중 하나만 갱신해도 두 줄을 같이 다시 찍는다 - "지금 ABB는 어떤
    상태고 관리자는 어떤 상태인지"를 매번 한 번에 볼 수 있게 하기 위함
    (한 줄만 따로 찍으면 이전 상태를 스크롤해서 찾아봐야 해서 가독성이
    떨어짐)."""

    def __init__(self):
        self.abb = ("대기 중입니다...", C.DIM)
        self.admin = ("대기 중입니다...", C.DIM)

    def render(self):
        abb_text, abb_color = self.abb
        admin_text, admin_color = self.admin
        print(f"{abb_color}● 현재 ABB에 {abb_text}{C.RESET}")
        print(f"{admin_color}● 현재 서버에 {admin_text}{C.RESET}")
        print()

    def set_abb(self, text, color):
        self.abb = (text, color)
        self.render()

    def set_admin(self, text, color):
        self.admin = (text, color)
        self.render()


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


def try_connect_once(host, port):
    """접속을 한 번만 시도 - 성공하면 소켓, 실패하면 None.
    메시지는 안 찍는다 (호출하는 쪽에서 StatusBoard로 보여줌)."""
    try:
        connection = socket.create_connection((host, port), timeout=10)
    except OSError:
        return None
    connection.settimeout(None)   # 연결 후에는 타임아웃 없이 계속 대기 가능하게 해제
    return connection


def connect_with_status(host, port, board, which, verb):
    """연결될 때까지 반복 시도하면서, 매 시도마다 StatusBoard의 해당 줄을
    갱신한다. which는 "abb" 또는 "admin" - board의 어느 줄을 갱신할지 결정.

    ABB Main(), 관리자 서버, 이 커넥터를 어떤 순서로 켜도 상관없다 - 상대가
    아직 안 켜져 있으면 이 함수가 뜰 때까지 재시도하며 기다린다."""
    setter = board.set_abb if which == "abb" else board.set_admin
    label = "ABB" if which == "abb" else "관리자 서버"

    attempt = 0
    while True:
        attempt += 1
        text = f"{verb}..." if attempt == 1 else f"{verb}...({attempt})"
        setter(text, C.YELLOW)

        connection = try_connect_once(host, port)
        if connection is not None:
            setter("접속됬습니다!", C.GREEN)
            print(f"{C.GREEN}✔ [{now()}] {label}에 연결되었습니다: {host}:{port}{C.RESET}\n")
            return connection

        time.sleep(RECONNECT_DELAY_SECONDS)


def run_connector(abb_host, abb_port, admin_host, admin_port, relay_name):
    """ABB, 관리자 순서로 접속한 뒤 관리자 명령을 그대로 ABB로 전달.

    두 접속 모두 상대가 아직 준비되지 않았으면 뜰 때까지 재시도하며 기다린다
    (connect_with_status).

    ABB와의 연결만 끊기면 관리자와의 연결은 그대로 둔 채 ABB 쪽만 재연결을
    시도한다 - 관리자 쪽에서 보면 이 중계기는 계속 접속된 상태로 남아있는다."""
    board = StatusBoard()
    board.render()

    abb_connection = connect_with_status(abb_host, abb_port, board, "abb", "접속 시도 중")
    admin_connection = connect_with_status(admin_host, admin_port, board, "admin", "접속중입니다")

    send_text(admin_connection, relay_name)   # 관리자에게 내 이름을 먼저 알림
    print(f"{C.CYAN}📡 관리자에게 이름을 알렸습니다: {relay_name}{C.RESET}")
    print(f"{C.BOLD}{C.GREEN}✅ 모든 연결 완료 - 이제부터 관리자 명령을 그대로 ABB로 전달합니다.{C.RESET}\n")

    admin_buffer = b""

    try:
        while True:
            command, admin_buffer = receive_line(admin_connection, admin_buffer)

            if command is None:
                print(f"{C.RED}✖ [{now()}] 관리자 서버와의 연결이 종료되었습니다.{C.RESET}")
                break

            print(f"{C.MAGENTA}[{now()}] 관리자 →{C.RESET} {command}")

            try:
                send_text(abb_connection, command)
                print(f"{C.CYAN}[{now()}]        → ABB 전달 완료{C.RESET}")
            except OSError as error:
                print(f"{C.RED}✖ [{now()}] ABB 연결이 끊겼습니다: {error}{C.RESET}")
                abb_connection.close()

                send_text(admin_connection, "ABB disconnected - reconnecting")
                abb_connection = connect_with_status(abb_host, abb_port, board, "abb", "재접속 시도 중")
                send_text(admin_connection, "ABB reconnected")

                send_text(abb_connection, command)   # 실패했던 명령을 재접속 후 다시 전달
                print(f"{C.CYAN}[{now()}]        → ABB 전달 완료 (재접속 후){C.RESET}")

            if command == QUIT_MESSAGE:
                print(f"{C.YELLOW}[{now()}] 중계기를 종료합니다.{C.RESET}")
                break

    except OSError as error:
        print()
        print(f"{C.RED}중계 중 연결 오류: {error}{C.RESET}")

    finally:
        admin_connection.close()
        abb_connection.close()


if __name__ == "__main__":
    print_banner()

    try:
        run_connector(ABB_HOST, ABB_PORT, ADMIN_HOST, ADMIN_PORT, RELAY_NAME)
    except KeyboardInterrupt:
        print()
        print(f"{C.YELLOW}중계기를 종료합니다.{C.RESET}")
