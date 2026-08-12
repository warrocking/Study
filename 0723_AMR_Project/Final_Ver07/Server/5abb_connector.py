# 5abb_V08.py (5abb_V07.py 기반, 3abb_V06.py와 같은 구조)
#
# 5abb 로봇 옆 노트북에서 실행하는 중계기 프로그램.
# 설정값이 이 파일 안에 이미 채워져 있으므로, 별도 설정 파일 없이 이 파일 하나만
# 그대로 실행하면 됩니다.
#
# V07 대비 이 버전에서 바뀐 것 (관리자 -> ABB 방향에도 버퍼 드레인 추가):
#   3abb_V06.py와 동일한 문제 - ABB -> 관리자 방향엔 드레인 루프가 있었는데
#   관리자 -> ABB 방향(예: "Start"/"AmrArrived" 명령 전달)엔 빠져 있었다.
#   관리자가 두 명령을 짧은 간격으로 보내서 커넥터의 recv() 한 번에 같이
#   들어오면, 두 번째 명령이 admin_buffer에 묻혀서 다음 관리자발 데이터가
#   올 때까지 ABB에 전달되지 않을 수 있었다(직접 재현 테스트로 확인 -
#   scratchpad/connector_admin_drain_test.py). 같은 방식으로 드레인 루프를
#   추가해서 고쳤다.
#
# V06 대비 이전 버전에서 바뀐 것 (관리자 재접속이 ABB 연결까지 끊던 버그 수정):
#   관리자 서버 연결이 끊기면(서버 재시작, 네트워크 순간 끊김 등) 이전에는
#   바깥 while True 루프를 통째로 다시 돌면서 finally에서 ABB 연결까지 같이
#   닫아버렸다. ABB(5abb.mod)는 아무 문제 없었는데 srv_client_socket이 갑자기
#   끊긴 것처럼 보이게 되고, WaitForAmrArrived의 ERROR 핸들러는
#   ERR_SOCK_TIMEOUT만 처리하므로 이 ERR_SOCK_CLOSED는 위로 전파돼서
#   Run_Socket_Server까지 올라가 소켓을 재생성하고 RETRY한다 - 그 과정에서
#   몇 번째 차량을 조립 중이었는지 같은 진행 상태가 전부 날아가고 Start 대기
#   상태로 리셋됐다("2번째 차량을 안 만들었다" 증상의 원인으로 추정).
#   이제 reconnect_admin()으로 관리자 쪽 연결만 따로 재접속하고, ABB 연결은
#   절대 건드리지 않는다.
#
# V05 대비 이 버전에서 바뀐 것 (수신 버퍼 드레인 버그 수정):
#   read_ready_line()은 한 번의 recv()로 완성된 줄을 하나만 꺼내 돌려줬는데,
#   5abb.mod가 이제 짧은 간격으로 여러 메시지(예: "ConveyDone" 직후 바로
#   "Done")를 연달아 보낼 수 있게 되면서, 한 번의 recv()에 개행이 여러 개
#   섞여 들어오는 경우가 생겼다. 이러면 select()는 이미 다 읽어온 소켓에
#   대해 다시 신호를 주지 않으므로, 버퍼에 남은 두 번째 줄이 영원히 처리되지
#   않고 묻히는 문제가 있었다. extract_line() 헬퍼로 recv() 없이 버퍼에서
#   완성된 줄을 계속 꺼내는 드레인 루프를 추가해서 고쳤다.
#
# V04와의 차이 (ABB -> 관리자 방향 신호 중계 추가):
#   V04까지는 "관리자 명령을 ABB로 전달"만 했지, ABB가 보내는 건 전혀 읽지
#   않았다(주석에도 "ABB로부터 뭔가를 읽어오지 않음"이라고 되어 있었음). 이제
#   ABB 쪽 RAPID 코드(5abb_V09.mod)가 작업 사이클 마지막에
#   SocketSend srv_client_socket \Str:="Done"; 으로 완료 신호를 보내기
#   시작했으므로, 이 커넥터도 그 신호를 받아서 관리자에게 그대로 전달해야
#   실제로 화면에 뜬다. select()로 관리자 소켓과 ABB 소켓을 동시에 지켜보다가
#   어느 쪽이든 데이터가 오면 그쪽을 처리하는 구조로 바꿨다 - 스레드 없이도
#   양방향을 동시에 볼 수 있다.
#
# 역할:
#   1) ABB 로봇(5abb_V09.mod)에 클라이언트로 접속
#   2) 총괄 관리자 서버(Server_admin.py)에 클라이언트로 접속
# 이후로는 select()로 두 연결을 동시에 지켜보면서:
#   - 관리자에게서 명령이 오면 그대로 ABB로 전달
#   - ABB에게서 메시지(예: 작업 완료 신호 "Done")가 오면 "ABB: <메시지>" 형태로
#     관리자에게 전달
# 을 반복한다.

import select
import socket
import sys
import time
import traceback
from datetime import datetime


RELAY_NAME = "5abb"

ABB_HOST = "192.168.3.3"
ABB_PORT = 5000

ADMIN_HOST = "100.109.178.123"   # desktop-12mccaq (서버장) Tailscale IP
ADMIN_PORT = 5000

ENCODING = "utf-8"
QUIT_MESSAGE = "/quit"

CONNECT_TIMEOUT_SECONDS = 5      # 접속 시도 1회당 최대 대기 시간 (너무 길면 Ctrl+C 반응도 늦어짐)
SEND_TIMEOUT_SECONDS = 5         # ABB로 명령 전송 시 최대 대기 시간
SELECT_TIMEOUT_SECONDS = 1.0     # select() 대기 시간 - Ctrl+C가 주기적으로 반응하게 함
RECONNECT_DELAY_SECONDS = 2      # 접속 실패 후 다음 재시도까지 대기 시간
HINT_AFTER_ATTEMPTS = 5          # 이만큼 연속 실패하면 문제 해결 힌트를 한 번 더 보여줌


# ===== 콘솔 호환성 설정 (Windows에서 한글 깨짐/크래시, 색상 미지원 방지) =====
# 근거: Python 버그 트래커 #41437(Windows 블로킹 소켓에서 Ctrl+C 지연),
# Windows Console 공식 문서(ENABLE_VIRTUAL_TERMINAL_PROCESSING 수동 활성화 필요),
# 다수의 "Windows 콘솔 cp949/cp1252 + 이모지 = UnicodeEncodeError" 사례들을
# 참고해서, 실행 환경(cmd.exe/PowerShell/Windows Terminal/VSCode 터미널 등)에
# 상관없이 최대한 안전하게 동작하도록 시작 시점에 아래를 전부 시도한다.

def _enable_windows_console_support():
    """Windows 콘솔에서 UTF-8 출력과 ANSI 색상이 최대한 잘 나오도록 시도한다.
    실패해도 예외를 던지지 않고 성공 여부만 반환한다 - 실패하면 아래에서
    색상 사용을 그냥 꺼버리는 판단 근거로만 쓴다."""
    if sys.platform != "win32":
        return True   # Windows가 아니면(리눅스/맥 터미널) 기본이 대부분 UTF-8 + ANSI 지원

    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)   # 콘솔이 UTF-8 바이트를 기대하도록 변경
        kernel32.SetConsoleCP(65001)

        STD_OUTPUT_HANDLE = -11
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        mode = ctypes.c_uint32()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        return bool(kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING))
    except Exception:
        return False


_CONSOLE_SUPPORTS_ANSI = _enable_windows_console_support()

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

USE_COLOR = _CONSOLE_SUPPORTS_ANSI and sys.stdout.isatty()


class C:
    RESET = "\033[0m" if USE_COLOR else ""
    BOLD = "\033[1m" if USE_COLOR else ""
    DIM = "\033[2m" if USE_COLOR else ""
    RED = "\033[91m" if USE_COLOR else ""
    GREEN = "\033[92m" if USE_COLOR else ""
    YELLOW = "\033[93m" if USE_COLOR else ""
    CYAN = "\033[96m" if USE_COLOR else ""
    MAGENTA = "\033[95m" if USE_COLOR else ""


TAG_OK = "[연결됨]"
TAG_ERR = "[오류]"
TAG_INFO = "[안내]"
TAG_DONE = "[작업완료]"


def now():
    return datetime.now().strftime("%H:%M:%S")


def print_banner():
    print(f"{C.BOLD}{C.CYAN}")
    print("=========================================")
    print(f"   {RELAY_NAME} 중계기 프로그램을 시작합니다")
    print("=========================================")
    print(C.RESET)
    if not USE_COLOR:
        print(f"{TAG_INFO} 이 콘솔에서는 색상을 못 켰습니다 - 색상 없이 진행합니다.\n")


class StatusBoard:
    """ABB / 관리자 서버 접속 상태를 항상 2줄로 같이 보여준다."""

    def __init__(self):
        self.abb = ("대기 중입니다...", C.DIM)
        self.admin = ("대기 중입니다...", C.DIM)

    def render(self):
        abb_text, abb_color = self.abb
        admin_text, admin_color = self.admin
        print(f"{abb_color}* 현재 ABB에 {abb_text}{C.RESET}")
        print(f"{admin_color}* 현재 서버에 {admin_text}{C.RESET}")
        print()

    def set_abb(self, text, color):
        self.abb = (text, color)
        self.render()

    def set_admin(self, text, color):
        self.admin = (text, color)
        self.render()


def send_text(connection, text):
    connection.sendall((text + "\n").encode(ENCODING))


def read_ready_line(connection, buffer):
    """select()로 이 연결에 데이터가 준비됐다고 확인된 직후 호출한다.
    recv 한 번으로 버퍼에 채워넣고, 완성된 줄(개행까지)이 있으면 그 줄을
    반환한다. 아직 줄이 안 끝났으면 line=None(계속 기다림), 연결이 끊겼으면
    closed=True를 반환한다.

    반환값: (line 또는 None, 갱신된 buffer, closed)."""
    try:
        chunk = connection.recv(4096)
    except OSError:
        return None, buffer, True
    if not chunk:
        return None, buffer, True

    buffer += chunk
    if b"\n" in buffer:
        line, _, rest = buffer.partition(b"\n")
        return line.decode(ENCODING).rstrip("\r"), rest, False
    return None, buffer, False


def extract_line(buffer):
    """이미 recv해서 buffer에 들어있는 데이터에서, 새로 recv하지 않고 완성된
    줄이 있으면 하나 꺼낸다. 한 번의 recv()로 개행이 여러 개 든 데이터가
    한꺼번에 들어올 수 있는데(예: ConveyDone 보내자마자 바로 Done), 그러면
    select()는 그 소켓에 대해 다시 신호를 주지 않는다 - 이미 다 읽어왔기
    때문이다. 그래서 select() 신호 없이도 buffer에 남은 줄을 마저 꺼내
    쓰기 위한 함수."""
    if b"\n" in buffer:
        line, _, rest = buffer.partition(b"\n")
        return line.decode(ENCODING).rstrip("\r"), rest
    return None, buffer


def try_connect_once(host, port):
    """접속을 한 번만 시도한다. 성공하면 (소켓, None), 실패하면 (None, 예외)를
    돌려준다."""
    try:
        connection = socket.create_connection((host, port), timeout=CONNECT_TIMEOUT_SECONDS)
    except OSError as error:
        return None, error
    connection.settimeout(None)   # 연결 후에는 타임아웃 없이 계속 대기 가능하게 해제
    return connection, None


def print_troubleshooting_hint(label, host, port, attempt):
    print(f"{C.YELLOW}{TAG_INFO} {label} 접속이 {attempt}번 연속 실패했습니다. 확인해보세요:{C.RESET}")
    print(f"{C.YELLOW}  1) 주소가 맞는지: {host}:{port}{C.RESET}")
    print(f"{C.YELLOW}  2) 네트워크(WiFi/랜선) 연결 상태{C.RESET}")
    print(f"{C.YELLOW}  3) 상대쪽 프로그램(ABB Main 또는 관리자 서버)이 실제로 켜져 있는지{C.RESET}")
    print(f"{C.YELLOW}  4) 처음 실행이라면 Windows 방화벽 허용 팝업이 뜨지 않았는지{C.RESET}")
    print()


def connect_with_status(host, port, board, which, verb):
    """연결될 때까지 반복 시도하면서, 매 시도마다 StatusBoard의 해당 줄을
    갱신한다. ABB Main(), 관리자 서버, 이 커넥터를 어떤 순서로 켜도 상관없다."""
    setter = board.set_abb if which == "abb" else board.set_admin
    label = "ABB" if which == "abb" else "관리자 서버"

    attempt = 0
    last_error_text = None
    while True:
        attempt += 1
        text = f"{verb}..." if attempt == 1 else f"{verb}...({attempt})"
        setter(text, C.YELLOW)

        connection, error = try_connect_once(host, port)
        if connection is not None:
            setter("접속됬습니다!", C.GREEN)
            print(f"{C.GREEN}{TAG_OK} [{now()}] {label}에 연결되었습니다: {host}:{port}{C.RESET}\n")
            return connection

        error_text = str(error)
        if error_text != last_error_text:
            print(f"{C.DIM}   ({type(error).__name__}: {error}){C.RESET}")
            last_error_text = error_text

        if attempt % HINT_AFTER_ATTEMPTS == 0:
            print_troubleshooting_hint(label, host, port, attempt)

        time.sleep(RECONNECT_DELAY_SECONDS)


def reconnect_abb(abb_host, abb_port, admin_connection, board):
    """ABB 재접속 - 재접속 전후로 관리자에게 상태 메시지를 보낸다(관리자 연결
    자체가 죽어있으면 그 전송은 조용히 무시하고 ABB 재접속만 계속 진행)."""
    try:
        send_text(admin_connection, "ABB disconnected - reconnecting")
    except OSError:
        pass

    abb_connection = connect_with_status(abb_host, abb_port, board, "abb", "재접속 시도 중")

    try:
        send_text(admin_connection, "ABB reconnected")
    except OSError:
        pass

    return abb_connection


def reconnect_admin(admin_host, admin_port, relay_name, board):
    """관리자 서버 재접속 - ABB 연결은 절대 건드리지 않는다. 3abb_V05.py의
    reconnect_admin()과 동일한 이유로 추가됨(관리자 재접속이 ABB 연결까지
    끊어서 진행 상태가 리셋되던 버그 수정)."""
    admin_connection = connect_with_status(admin_host, admin_port, board, "admin", "재접속중입니다")
    send_text(admin_connection, relay_name)
    print(f"{C.CYAN}{TAG_INFO} 관리자에게 이름을 다시 알렸습니다: {relay_name}{C.RESET}")
    return admin_connection


def run_connector(abb_host, abb_port, admin_host, admin_port, relay_name):
    """접속 -> 양방향 중계 -> (관리자가 끊기면) 재접속을 계속 반복한다.

    select()로 admin_connection과 abb_connection을 동시에 지켜본다:
      - 관리자 쪽에 데이터가 오면 -> 그대로 ABB로 전달
      - ABB 쪽에 데이터가 오면(예: 작업 완료 신호) -> "ABB: <메시지>" 형태로
        관리자에게 전달
    이 함수에서 빠져나가는 경우는 딱 두 가지뿐이다: 관리자에게서 "/quit"을
    받거나, 사용자가 Ctrl+C를 누를 때."""
    while True:
        board = StatusBoard()
        board.render()

        abb_connection = connect_with_status(abb_host, abb_port, board, "abb", "접속 시도 중")
        admin_connection = connect_with_status(admin_host, admin_port, board, "admin", "접속중입니다")

        send_text(admin_connection, relay_name)   # 관리자에게 내 이름을 먼저 알림
        print(f"{C.CYAN}{TAG_INFO} 관리자에게 이름을 알렸습니다: {relay_name}{C.RESET}")
        print(f"{C.BOLD}{C.GREEN}{TAG_OK} 모든 연결 완료 - 양방향 중계를 시작합니다.{C.RESET}\n")

        admin_buffer = b""
        abb_buffer = b""
        should_quit = False

        try:
            while True:
                readable, _, _ = select.select(
                    [admin_connection, abb_connection], [], [], SELECT_TIMEOUT_SECONDS
                )

                def relay_abb_message(message):
                    if message.strip().lower() == "done":
                        print(f"{C.BOLD}{C.GREEN}{TAG_DONE} [{now()}] ABB -> {C.RESET}{message}")
                    else:
                        print(f"{C.CYAN}[{now()}] ABB ->{C.RESET} {message}")
                    try:
                        send_text(admin_connection, f"ABB: {message}")
                    except OSError as error:
                        print(f"{C.RED}{TAG_ERR} 관리자에게 전달 실패: {error}{C.RESET}")

                if abb_connection in readable:
                    message, abb_buffer, closed = read_ready_line(abb_connection, abb_buffer)
                    if closed:
                        print(f"{C.RED}{TAG_ERR} [{now()}] ABB 연결이 끊겼습니다.{C.RESET}")
                        abb_connection.close()
                        abb_connection = reconnect_abb(abb_host, abb_port, admin_connection, board)
                        abb_buffer = b""
                    elif message is not None:
                        relay_abb_message(message)

                        # 방금 recv() 한 번에 개행이 여러 개 섞여 들어왔을 수
                        # 있다(예: ConveyDone 직후 바로 Done). select()는 이미
                        # 읽어온 데이터에 대해서는 다시 신호를 안 주므로, 여기서
                        # buffer에 남은 완성된 줄을 전부 마저 처리한다.
                        while True:
                            extra, abb_buffer = extract_line(abb_buffer)
                            if extra is None:
                                break
                            relay_abb_message(extra)

                if admin_connection in readable:
                    def relay_admin_command(command):
                        nonlocal abb_connection, abb_buffer, should_quit
                        print(f"{C.MAGENTA}[{now()}] 관리자 ->{C.RESET} {command}")

                        try:
                            abb_connection.settimeout(SEND_TIMEOUT_SECONDS)
                            send_text(abb_connection, command)
                            print(f"{C.CYAN}[{now()}]        -> ABB 전달 완료{C.RESET}")
                        except OSError as error:
                            print(f"{C.RED}{TAG_ERR} [{now()}] ABB 연결이 끊겼습니다: "
                                  f"{type(error).__name__}: {error}{C.RESET}")
                            abb_connection.close()
                            abb_connection = reconnect_abb(abb_host, abb_port, admin_connection, board)
                            abb_buffer = b""

                            try:
                                send_text(abb_connection, command)   # 실패했던 명령을 재접속 후 다시 전달
                                print(f"{C.CYAN}[{now()}]        -> ABB 전달 완료 (재접속 후){C.RESET}")
                            except OSError as error:
                                print(f"{C.RED}{TAG_ERR} 재접속 직후 전달도 실패했습니다: {error}{C.RESET}")

                        if command == QUIT_MESSAGE:
                            print(f"{C.YELLOW}[{now()}] 관리자로부터 종료 명령을 받아 "
                                  f"중계기를 종료합니다.{C.RESET}")
                            should_quit = True

                    command, admin_buffer, closed = read_ready_line(admin_connection, admin_buffer)

                    if closed:
                        print(f"{C.RED}{TAG_ERR} [{now()}] 관리자 서버와의 연결이 종료되었습니다. "
                              f"ABB 연결은 그대로 두고 관리자만 다시 접속합니다.{C.RESET}\n")
                        admin_connection.close()
                        admin_connection = reconnect_admin(admin_host, admin_port, relay_name, board)
                        admin_buffer = b""
                        continue

                    if command is not None:
                        relay_admin_command(command)

                        # v08: ABB -> 관리자 방향엔 진작 드레인 루프가 있었는데
                        # (위 abb_connection 처리 참고), 관리자 -> ABB 방향엔 빠져
                        # 있었다. 한 번의 recv()에 명령이 여러 줄 섞여 들어오면
                        # select()가 이미 다 읽어온 소켓엔 다시 신호를 안 주므로,
                        # admin_buffer에 남은 두 번째 줄이 다음 관리자발 데이터가
                        # 올 때까지 무한정 묻힐 수 있었다. 같은 방식으로 버퍼에
                        # 남은 줄을 전부 마저 꺼내 전달한다.
                        while not should_quit:
                            extra, admin_buffer = extract_line(admin_buffer)
                            if extra is None:
                                break
                            relay_admin_command(extra)

                        if should_quit:
                            break

        except OSError as error:
            print()
            print(f"{C.RED}{TAG_ERR} 중계 중 연결 오류: {type(error).__name__}: {error}{C.RESET}\n")

        finally:
            admin_connection.close()
            abb_connection.close()

        if should_quit:
            return

        print(f"{C.YELLOW}{RECONNECT_DELAY_SECONDS}초 후 처음부터 다시 접속을 시도합니다...{C.RESET}\n")
        time.sleep(RECONNECT_DELAY_SECONDS)


if __name__ == "__main__":
    print_banner()

    try:
        run_connector(ABB_HOST, ABB_PORT, ADMIN_HOST, ADMIN_PORT, RELAY_NAME)
    except KeyboardInterrupt:
        print()
        print(f"{C.YELLOW}Ctrl+C가 눌려서 중계기를 종료합니다.{C.RESET}")
    except Exception:
        print()
        print(f"{C.RED}{TAG_ERR} 예상하지 못한 오류가 발생했습니다:{C.RESET}")
        print(f"{C.RED}{traceback.format_exc()}{C.RESET}")
        try:
            input("확인했으면 Enter를 눌러 창을 닫으세요...")
        except (EOFError, KeyboardInterrupt):
            pass
