# Server_5abb_version4.py
#
# 5abb 로봇 옆 노트북에서 실행하는 중계기 프로그램 (V4 - 실행 환경 호환성 강화판).
# 설정값이 이 파일 안에 이미 채워져 있으므로, 별도 설정 파일 없이 이 파일 하나만
# 그대로 실행하면 됩니다.
#
# V3와의 차이 (실행 환경/터미널 설정에 따라 결과가 달라지는 문제들을 최대한 없앰):
#   1) 한글/색상이 깨지거나 크래시 나는 문제
#      Windows 콘솔은 기본 코드페이지가 cp949/cp1252 등이라, 그냥 이모지나
#      박스 문자를 출력하면 UnicodeEncodeError로 죽거나 글자가 깨질 수 있다.
#      이 파일은 시작할 때 콘솔 코드페이지를 UTF-8(65001)로 직접 바꾸고,
#      sys.stdout도 UTF-8로 강제 설정한다(그래도 안 되는 글자는 죽는 대신
#      물음표로 대체). 이모지/박스 문자 같은 "인코딩은 맞아도 글꼴에 그림이
#      없어서 네모로 깨질 수 있는" 문자는 아예 안 쓰고, 어디서나 보이는
#      일반 문자([연결됨], *, = 등)만 사용한다.
#   2) 색상이 이스케이프 코드 글자 그대로 보이는 문제
#      cmd.exe는 ANSI 색상을 켜주기 전까지는 "\033[92m" 같은 코드가 화면에
#      글자로 그대로 찍힌다. 이 파일은 시작할 때 Windows 콘솔의 가상 터미널
#      모드를 켜보고, 실패하면(구형 콘솔 등) 색상 자체를 안 쓰도록 자동으로
#      전환한다 - 실행하는 사람이 뭘 설정할 필요가 없다.
#   3) 관리자 서버 연결이 끊기면 프로그램이 조용히 끝나버리던 문제
#      V3까지는 관리자 서버와의 연결이 끊기면 그 자리에서 프로그램이 끝났다.
#      이제는 "/quit"을 받거나 Ctrl+C를 누르기 전까지는 절대 끝나지 않고,
#      끊기면 처음부터(ABB/관리자 둘 다) 다시 접속을 시도한다.
#   4) 문제가 생겼을 때 원인을 알기 어려운 문제
#      접속 실패마다 파이썬 예외의 종류와 내용을 그대로 보여주고, 같은 곳에서
#      5번 연속 실패하면 확인해볼 것(주소, 네트워크, 상대 프로그램, 방화벽)을
#      한 번 더 안내한다. 예상 못한 에러가 나도 창이 바로 안 닫히고, 원인을
#      보여준 뒤 Enter를 눌러야 닫히게 했다 - 더블클릭으로 실행했을 때 에러가
#      뜨자마자 창이 사라져서 아무것도 못 보는 문제를 막기 위함.
#   5) Ctrl+C 응답성 / 접속 지연 표시
#      V2/V3와 같은 원리(짧은 타임아웃 반복)로 Ctrl+C가 잘 먹히게 하고,
#      접속 시도 1회당 최대 대기 시간도 10초 -> 5초로 줄여서 Ctrl+C가 최악의
#      경우에도 더 빨리 반응하고, 재시도 화면도 더 자주 갱신되게 했다.
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
    색상 사용을 그냥 꺼버리는 판단 근거로만 쓴다 (VSCode 통합 터미널의
    프로필 설정이 cmd/PowerShell/Git Bash 중 무엇이든, 이 함수가 실행
    환경을 스스로 맞추므로 결과가 VSCode 설정에 따라 달라지지 않는다)."""
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

# 콘솔 코드페이지를 못 바꿨더라도(더 드문 경우), 파이썬이 자체적으로 출력을
# UTF-8로 인코딩하도록 강제 - errors="replace"로 그래도 안 되는 글자는
# 프로그램이 죽는 대신 물음표로만 대체되게 하는 최후의 안전장치.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# 색상은 "ANSI를 지원하는 콘솔"이면서 "진짜 터미널에 출력 중일 때"만 사용한다.
# 파일로 리다이렉트하거나 ANSI 미지원 콘솔이면, 색상 이스케이프 코드가 그대로
# 글자로 보이는 것을 막기 위해 색상 자체를 끈다.
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


# 이모지/박스 문자(═, ✔, 📡 등)는 인코딩이 맞아도 콘솔 글꼴에 그림 자체가 없어서
# 네모(tofu)로 깨질 수 있다 - 이건 인코딩 문제가 아니라 글꼴 문제라 코드로
# 감지/보정이 불가능하므로, 아예 어디서나 보이는 일반 문자만 사용한다.
TAG_OK = "[연결됨]"
TAG_ERR = "[오류]"
TAG_INFO = "[안내]"


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
    """ABB / 관리자 서버 접속 상태를 항상 2줄로 같이 보여준다.

    둘 중 하나만 갱신해도 두 줄을 같이 다시 찍는다 - "지금 ABB는 어떤
    상태고 관리자는 어떤 상태인지"를 매번 한 번에 볼 수 있게 하기 위함."""

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


def receive_line(connection, buffer, timeout_seconds=1.0):
    """관리자 연결에서 한 줄(개행까지)을 읽는다 - 짧은 타임아웃을 계속 반복해서
    기다리기 때문에, 명령이 하나도 안 와도 주기적으로 파이썬 인터프리터로
    제어가 돌아온다. 타임아웃 없이 통짜로 블로킹해서 기다리면 Windows에서
    Ctrl+C(KeyboardInterrupt)가 그 blocking recv가 끝날 때까지 전달이
    미뤄지는 경우가 있어서(Python 버그 트래커 #41437), 명령이 없을 때
    Ctrl+C가 안 먹히는 원인이었다. buffer는 이전 호출에서 개행 뒤에 남은
    바이트를 다음 호출로 넘기기 위한 값으로, 호출할 때마다 반환값으로
    갱신해서 다시 넘겨야 한다.

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
    """접속을 한 번만 시도한다. 성공하면 (소켓, None), 실패하면 (None, 예외)를
    돌려준다 - 예외 객체를 그대로 넘겨서 호출하는 쪽이 "왜" 실패했는지
    구체적으로 보여줄 수 있게 한다."""
    try:
        connection = socket.create_connection((host, port), timeout=CONNECT_TIMEOUT_SECONDS)
    except OSError as error:
        return None, error
    connection.settimeout(None)   # 연결 후에는 타임아웃 없이 계속 대기 가능하게 해제
    return connection, None


def print_troubleshooting_hint(label, host, port, attempt):
    """같은 대상 접속이 여러 번 연속 실패했을 때만 한 번씩 보여주는 안내문 -
    매 시도마다 반복하면 화면이 도배되므로 HINT_AFTER_ATTEMPTS 간격으로만."""
    print(f"{C.YELLOW}{TAG_INFO} {label} 접속이 {attempt}번 연속 실패했습니다. 확인해보세요:{C.RESET}")
    print(f"{C.YELLOW}  1) 주소가 맞는지: {host}:{port}{C.RESET}")
    print(f"{C.YELLOW}  2) 네트워크(WiFi/랜선) 연결 상태{C.RESET}")
    print(f"{C.YELLOW}  3) 상대쪽 프로그램(ABB Main 또는 관리자 서버)이 실제로 켜져 있는지{C.RESET}")
    print(f"{C.YELLOW}  4) 처음 실행이라면 Windows 방화벽 허용 팝업이 뜨지 않았는지{C.RESET}")
    print()


def connect_with_status(host, port, board, which, verb):
    """연결될 때까지 반복 시도하면서, 매 시도마다 StatusBoard의 해당 줄을
    갱신한다. which는 "abb" 또는 "admin" - board의 어느 줄을 갱신할지 결정.

    ABB Main(), 관리자 서버, 이 커넥터를 어떤 순서로 켜도 상관없다 - 상대가
    아직 안 켜져 있으면 이 함수가 뜰 때까지 재시도하며 기다린다."""
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
            # 실패 원인이 바뀌었을 때만(혹은 처음 한 번) 구체적인 예외 내용을
            # 보여준다 - 매번 똑같은 메시지를 반복 출력해서 화면을 도배하지
            # 않으면서도, 원인이 바뀌면(거부 -> 타임아웃 등) 바로 알 수 있게.
            print(f"{C.DIM}   ({type(error).__name__}: {error}){C.RESET}")
            last_error_text = error_text

        if attempt % HINT_AFTER_ATTEMPTS == 0:
            print_troubleshooting_hint(label, host, port, attempt)

        time.sleep(RECONNECT_DELAY_SECONDS)


def run_connector(abb_host, abb_port, admin_host, admin_port, relay_name):
    """접속 -> 중계 -> (관리자가 끊기면) 재접속을 계속 반복한다.

    ABB Main(), 관리자 서버, 이 커넥터를 어떤 순서로 켜도 되고, 관리자 서버가
    도중에 재시작되어도 이 프로그램을 다시 켤 필요 없이 자동으로 복구된다.
    이 함수에서 빠져나가는 경우는 딱 두 가지뿐이다: 관리자에게서 "/quit"을
    받거나, 사용자가 Ctrl+C를 누를 때(KeyboardInterrupt는 이 함수를 호출한
    쪽에서 처리)."""
    while True:
        board = StatusBoard()
        board.render()

        abb_connection = connect_with_status(abb_host, abb_port, board, "abb", "접속 시도 중")
        admin_connection = connect_with_status(admin_host, admin_port, board, "admin", "접속중입니다")

        send_text(admin_connection, relay_name)   # 관리자에게 내 이름을 먼저 알림
        print(f"{C.CYAN}{TAG_INFO} 관리자에게 이름을 알렸습니다: {relay_name}{C.RESET}")
        print(f"{C.BOLD}{C.GREEN}{TAG_OK} 모든 연결 완료 - 이제부터 관리자 명령을 그대로 ABB로 전달합니다.{C.RESET}\n")

        admin_buffer = b""
        should_quit = False

        try:
            while True:
                command, admin_buffer = receive_line(admin_connection, admin_buffer)

                if command is None:
                    print(f"{C.RED}{TAG_ERR} [{now()}] 관리자 서버와의 연결이 종료되었습니다. "
                          f"다시 접속을 시도합니다.{C.RESET}\n")
                    break

                print(f"{C.MAGENTA}[{now()}] 관리자 ->{C.RESET} {command}")

                try:
                    abb_connection.settimeout(SEND_TIMEOUT_SECONDS)
                    send_text(abb_connection, command)
                    print(f"{C.CYAN}[{now()}]        -> ABB 전달 완료{C.RESET}")
                except OSError as error:
                    print(f"{C.RED}{TAG_ERR} [{now()}] ABB 연결이 끊겼습니다: "
                          f"{type(error).__name__}: {error}{C.RESET}")
                    abb_connection.close()

                    try:
                        send_text(admin_connection, "ABB disconnected - reconnecting")
                    except OSError:
                        pass   # 관리자 연결도 같이 끊긴 상태일 수 있음 - ABB 재연결은 계속 진행

                    abb_connection = connect_with_status(abb_host, abb_port, board, "abb", "재접속 시도 중")

                    try:
                        send_text(admin_connection, "ABB reconnected")
                        send_text(abb_connection, command)   # 실패했던 명령을 재접속 후 다시 전달
                        print(f"{C.CYAN}[{now()}]        -> ABB 전달 완료 (재접속 후){C.RESET}")
                    except OSError as error:
                        print(f"{C.RED}{TAG_ERR} 관리자 연결도 끊긴 상태로 보입니다: {error}{C.RESET}")

                if command == QUIT_MESSAGE:
                    print(f"{C.YELLOW}[{now()}] 관리자로부터 종료 명령을 받아 중계기를 종료합니다.{C.RESET}")
                    should_quit = True
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
        # 예상하지 못한 에러가 나도 원인을 보여준 뒤 창이 바로 닫히지 않게 한다 -
        # 더블클릭으로 실행했을 때 에러가 뜨자마자 창이 사라져서 아무것도 못
        # 보는 문제를 막기 위함.
        print()
        print(f"{C.RED}{TAG_ERR} 예상하지 못한 오류가 발생했습니다:{C.RESET}")
        print(f"{C.RED}{traceback.format_exc()}{C.RESET}")
        try:
            input("확인했으면 Enter를 눌러 창을 닫으세요...")
        except (EOFError, KeyboardInterrupt):
            pass
