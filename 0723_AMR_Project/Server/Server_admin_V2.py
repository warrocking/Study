# Server_admin_V2.py (Server_admin.py 기반)
#
# 총괄(관리자) 노트북에서 실행하는 서버 - 제가 직접 실행하는 파일입니다.
#
# V1과의 차이 (화면이 로그로 도배되는 문제 해결):
#   3abb/4abb/5abb/amr 등 여러 대가 각자 30초 간격으로(서로 안 맞춰서) 상태
#   메시지(HEARTBEAT/STATUS)를 보내다 보니, 명령을 입력하는 중에도 그 사이에
#   끼어들면서 화면이 금방 로그로 뒤덮이는 문제가 있었다. 이 버전은 화면
#   위쪽 몇 줄을 "고정 상태판"으로 예약해서, HEARTBEAT/STATUS처럼 반복되는
#   흔한 신호는 그 자리에서 계속 덮어쓰기만 하고 스크롤되는 로그에는 안
#   찍히게 했다. 연결/끊김/작업완료/에러/명령 전송처럼 드물고 중요한 일만
#   기존처럼 로그에 남는다.
#
#   외부 라이브러리(rich, curses 등)는 설치가 필요해서 "파일 하나만 받아서
#   그대로 실행" 원칙이 깨지므로 안 쓰고, 표준 ANSI 이스케이프 코드만으로
#   구현했다 - 특히 "스크롤 영역 지정"(DECSTBM, \033[상단;하단r)을 써서
#   상태판이 있는 윗줄들은 아예 스크롤 대상에서 빼버렸다. 그래서 로그가
#   아무리 쌓여도 상태판 줄은 절대 밀려나지 않고, 반대로 상태판을 갱신해도
#   지금 입력 중인 명령 줄이 흐트러지지 않는다. ANSI를 못 켜는 콘솔에서는
#   이 기능 전체를 끄고 V1과 똑같이 동작한다(안전한 폴백).
#
# 나머지는 V1과 동일:
#   - Windows 콘솔 코드페이지/ANSI 색상 모드 자동 설정
#   - 예상하지 못한 에러가 나도 창이 바로 안 닫힘
#   - 명령 입력 형식: "이름 명령" (예: "5abb Start"), 전체는 "all 명령", 종료는 "/quit"
#
# 실행 (VSCode 통합 터미널, PowerShell, cmd.exe 어디서든 동일하게 동작):
#     python Server_admin_V2.py

import shutil
import socket
import sys
import threading
import traceback
from datetime import datetime


HOST = "0.0.0.0"   # 모든 인터페이스에서 접속을 받음 - Tailscale, 일반 LAN 둘 다 동작
PORT = 5000
ENCODING = "utf-8"
QUIT_MESSAGE = "/quit"
BROADCAST_NAME = "all"

connections_lock = threading.Lock()
connections = {}   # 중계기 이름 -> 연결 소켓
stop_event = threading.Event()   # 종료 신호 - accept_loop가 주기적으로 확인함


# ===== 콘솔 호환성 설정 (Windows에서 한글 깨짐/크래시, 색상 미지원 방지) =====
def _enable_windows_console_support():
    """Windows 콘솔에서 UTF-8 출력과 ANSI 색상이 최대한 잘 나오도록 시도한다.
    실패해도 예외를 던지지 않고 성공 여부만 반환한다 - 실패하면 아래에서
    색상/상태판 기능을 그냥 꺼버리는 판단 근거로만 쓴다."""
    if sys.platform != "win32":
        return True

    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)
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
# 상태판(고정 스크롤 영역)은 색상/ANSI가 되는 진짜 터미널에서만 켠다 - 파일로
# 리다이렉트하거나 ANSI 미지원 콘솔이면 그냥 V1과 같은 방식(전부 로그로 출력)으로
# 동작한다.
USE_DASHBOARD = USE_COLOR


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
TAG_ERR = "[끊김]"
TAG_INFO = "[안내]"
TAG_SEND = "[전송]"
TAG_DONE = "[작업완료]"

DONE_KEYWORD = "done"

# 상태판에 미리 자리를 배정해 둘 이름들 - 이 순서대로 위쪽에 줄이 고정된다.
# 목록에 없는 이름이 접속하면 EXTRA_SLOTS만큼 남는 빈 자리에 자동으로 배정됨.
KNOWN_RELAYS = ["3abb", "4abb", "5abb", "amr"]
EXTRA_SLOTS = 3

# 이 문자열로 "시작하는" 상태 메시지는 흔히 반복되는 신호로 보고 상태판만
# 갱신하고 로그(스크롤 영역)에는 안 찍는다. 그 외(ONLINE, ERR, 그 밖의 모든
# 메시지)는 지금까지처럼 로그에도 남는다.
ROUTINE_PREFIXES = ("heartbeat", "status")


def now():
    return datetime.now().strftime("%H:%M:%S")


def is_routine_status(message):
    lowered = message.strip().lower()
    return lowered.startswith(ROUTINE_PREFIXES)


def _terminal_size():
    size = shutil.get_terminal_size(fallback=(100, 30))
    return size.columns, size.lines


def _truncate(text, width):
    if len(text) <= width:
        return text
    return text[: max(0, width - 1)] + "…" if width > 1 else text[:width]


class Dashboard:
    """화면 위쪽 몇 줄을 상태판으로 고정하고, 그 아래는 ANSI 스크롤 영역
    (DECSTBM)으로 지정해서 로그/입력이 아무리 쌓여도 상태판 줄은 절대
    밀리지 않게 한다. 상태판 갱신도 커서를 저장했다가 정확히 그 줄만
    지우고 다시 쓴 뒤 원래 위치로 복귀하므로, 지금 입력 중인 명령 줄은
    전혀 건드리지 않는다."""

    def __init__(self, known_names, extra_slots):
        self.lock = threading.Lock()
        self.slots = list(known_names)
        self.extra_slots = extra_slots
        self.extra_names = []
        self.header_lines = 2          # 제목 줄 + 빈 줄
        self.panel_rows = len(self.slots) + self.extra_slots
        self.footer_lines = 1          # 구분선
        self.top_reserved = self.header_lines + self.panel_rows + self.footer_lines
        self.cols, _ = _terminal_size()

    def setup(self):
        if not USE_DASHBOARD:
            return
        cols, rows = _terminal_size()
        self.cols = cols
        sys.stdout.write("\033[2J\033[H")   # 화면 지우고 커서를 맨 위로

        sys.stdout.write(f"{C.BOLD}{C.CYAN}관리자 서버 - 연결 현황{C.RESET}\n\n")
        for name in self.slots:
            self._write_row_text(name, "대기 중입니다...", C.DIM)
        for i in range(self.extra_slots):
            sys.stdout.write("\n")
        sys.stdout.write(f"{C.DIM}{'-' * min(60, cols)}{C.RESET}\n")

        # 상태판(위 top_reserved줄) 아래부터만 스크롤되게 지정
        sys.stdout.write(f"\033[{self.top_reserved + 1};{rows}r")
        sys.stdout.write(f"\033[{self.top_reserved + 1};1H")
        sys.stdout.flush()

    def _row_index_for(self, name):
        if name in self.slots:
            return self.slots.index(name)
        if name not in self.extra_names:
            if len(self.extra_names) >= self.extra_slots:
                return None   # 여분 자리도 다 찼으면 상태판에는 못 올림 (로그로만 표시됨)
            self.extra_names.append(name)
        return len(self.slots) + self.extra_names.index(name)

    def _write_row_text(self, name, text, color):
        line = _truncate(f"{name:<8} {text}", self.cols - 1)
        sys.stdout.write(f"{color}{line}{C.RESET}\n")

    def update(self, name, text, color):
        if not USE_DASHBOARD:
            return
        with self.lock:
            idx = self._row_index_for(name)
            if idx is None:
                return
            row = self.header_lines + idx + 1
            line = _truncate(f"{name:<8} {text}", self.cols - 1)
            # 커서 저장 -> 해당 줄로 이동해서 지우고 다시 씀 -> 커서 복귀
            sys.stdout.write("\033[s")
            sys.stdout.write(f"\033[{row};1H\033[2K")
            sys.stdout.write(f"{color}{line}{C.RESET}")
            sys.stdout.write("\033[u")
            sys.stdout.flush()


dashboard = Dashboard(KNOWN_RELAYS, EXTRA_SLOTS)


def print_banner():
    if USE_DASHBOARD:
        dashboard.setup()
        if not USE_COLOR:
            print(f"{TAG_INFO} 이 콘솔에서는 색상을 못 켰습니다 - 색상 없이 진행합니다.\n")
        print(f"{C.DIM}명령 입력 형식: '이름 명령' (예: '5abb Start') / 전체: 'all 명령' / "
              f"종료: '/quit'{C.RESET}\n")
        return

    print(f"{C.BOLD}{C.CYAN}")
    print("=========================================")
    print("   관리자 서버를 시작합니다")
    print("=========================================")
    print(C.RESET)
    if not USE_COLOR:
        print(f"{TAG_INFO} 이 콘솔에서는 색상을 못 켰습니다 - 색상 없이 진행합니다.\n")
    print(f"{C.DIM}명령 입력 형식: '이름 명령' (예: '5abb Start') / 전체: 'all 명령' / "
          f"종료: '/quit'{C.RESET}\n")


def send_text(connection, text):
    connection.sendall((text + "\n").encode(ENCODING))


def receive_text(reader):
    line = reader.readline()
    if line == "":
        return None
    return line.rstrip("\r\n")


def accept_loop(server_socket):
    """새 중계기 접속을 계속 받아서 이름별로 등록하는 백그라운드 스레드."""
    while not stop_event.is_set():
        try:
            connection, address = server_socket.accept()
        except socket.timeout:
            continue
        except OSError:
            break

        threading.Thread(
            target=register_connection, args=(connection, address), daemon=True
        ).start()


def register_connection(connection, address):
    """새로 accept된 연결 하나의 등록을 전담하는 스레드."""
    connection.settimeout(5.0)
    reader = connection.makefile("r", encoding=ENCODING, newline="\n")
    try:
        name = receive_text(reader)
    except socket.timeout:
        name = None
    connection.settimeout(None)

    if not name:
        print(f"\n{C.YELLOW}{TAG_INFO} [{now()}] 알 수 없는 접속({address}) - "
              f"이름을 안 보내서 연결을 닫습니다.{C.RESET}")
        connection.close()
        return

    with connections_lock:
        connections[name] = connection

    dashboard.update(name, f"{now()}  연결됨", C.GREEN)
    print(f"\n{C.GREEN}{TAG_OK} [{now()}] {name} 연결됨: {address}{C.RESET}")
    read_status_loop(name, connection, reader)


def read_status_loop(name, connection, reader):
    """등록 이후 그 중계기가 보내는 상태 메시지를 계속 읽는다.

    HEARTBEAT/STATUS처럼 흔히 반복되는 신호는 상태판만 갱신하고 로그에는
    안 남긴다 - 30초 간격으로 여러 대가 제각각 보내다 보니 이게 그대로
    로그에 쌓이면 화면이 금방 뒤덮이고, 명령을 입력하는 중에도 끼어들어서
    불편했기 때문이다. 작업 완료 신호/ONLINE/ERR 등 드물고 중요한 메시지는
    지금까지처럼 로그에도 남는다."""
    try:
        while True:
            message = receive_text(reader)
            if message is None:
                break

            lowered = message.lower()

            if DONE_KEYWORD in lowered:
                dashboard.update(name, f"{now()}  {message}", C.BOLD + C.GREEN)
                print(f"\n{C.BOLD}{C.GREEN}{TAG_DONE} [{now()}] {name} 작업 완료!{C.RESET} "
                      f"{C.DIM}({message}){C.RESET}")
            elif is_routine_status(message):
                dashboard.update(name, f"{now()}  {message}", C.CYAN)
                # 로그에는 일부러 안 찍음 - 상태판에서만 계속 갱신됨
            elif "err" in lowered:
                dashboard.update(name, f"{now()}  {message}", C.RED)
                print(f"\n{C.RED}{TAG_ERR} [{now()}] {name} 상태:{C.RESET} {message}")
            else:
                dashboard.update(name, f"{now()}  {message}", C.CYAN)
                print(f"\n{C.CYAN}[{now()}] {name} 상태:{C.RESET} {message}")
    except OSError:
        pass
    finally:
        with connections_lock:
            if connections.get(name) is connection:
                connections.pop(name, None)
        dashboard.update(name, f"{now()}  연결 끊김", C.RED)
        print(f"\n{C.RED}{TAG_ERR} [{now()}] {name} 연결이 끊겼습니다.{C.RESET}")


def send_to(name, command):
    """지정한 이름(또는 'all')에게 명령을 전송. 끊긴 연결은 목록에서 제거."""
    with connections_lock:
        if name.lower() == BROADCAST_NAME:
            targets = list(connections.items())
        elif name in connections:
            targets = [(name, connections[name])]
        else:
            known = ", ".join(connections.keys()) if connections else "(없음)"
            print(f"{C.YELLOW}{TAG_INFO} '{name}'은(는) 현재 연결되어 있지 않습니다. "
                  f"현재 접속: {known}{C.RESET}")
            return

    if not targets:
        print(f"{C.YELLOW}{TAG_INFO} 현재 연결된 중계기가 없습니다.{C.RESET}")
        return

    for target_name, connection in targets:
        try:
            send_text(connection, command)
            print(f"{C.MAGENTA}{TAG_SEND} [{now()}] {target_name} ->{C.RESET} {command}")
        except OSError as error:
            print(f"{C.RED}{TAG_ERR} [{now()}] {target_name} 전송 실패: "
                  f"{type(error).__name__}: {error}{C.RESET}")
            with connections_lock:
                connections.pop(target_name, None)


def run_admin_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen()
    server_socket.settimeout(1.0)

    threading.Thread(target=accept_loop, args=(server_socket,), daemon=True).start()
    print(f"{C.GREEN}{TAG_OK} [{now()}] 중계기 접속을 기다리고 있습니다 "
          f"(포트 {port}, 여러 대 동시 접속 가능).{C.RESET}\n")

    try:
        while True:
            raw = input(f"{C.BOLD}[관리자]{C.RESET} 명령 입력: ")

            if raw.strip() == QUIT_MESSAGE:
                print(f"{C.YELLOW}[{now()}] 관리자 서버를 종료합니다.{C.RESET}")
                break

            parts = raw.split(maxsplit=1)
            if len(parts) != 2:
                print(f"{C.YELLOW}형식: '이름 명령' (예: '5abb Start') 또는 'all 명령'{C.RESET}")
                continue

            name, command = parts
            send_to(name, command)
    finally:
        stop_event.set()
        with connections_lock:
            for connection in connections.values():
                connection.close()
            connections.clear()
        server_socket.close()
        if USE_DASHBOARD:
            # 스크롤 영역 제한을 풀어서 종료 후 터미널이 정상적으로 돌아오게 함
            rows = _terminal_size()[1]
            sys.stdout.write(f"\033[1;{rows}r\033[{rows};1H")
            sys.stdout.flush()


if __name__ == "__main__":
    print_banner()

    try:
        run_admin_server(HOST, PORT)
    except KeyboardInterrupt:
        print()
        print(f"{C.YELLOW}Ctrl+C가 눌려서 관리자 서버를 종료합니다.{C.RESET}")
    except Exception:
        print()
        print(f"{C.RED}{TAG_ERR} 예상하지 못한 오류가 발생했습니다:{C.RESET}")
        print(f"{C.RED}{traceback.format_exc()}{C.RESET}")
        try:
            input("확인했으면 Enter를 눌러 창을 닫으세요...")
        except (EOFError, KeyboardInterrupt):
            pass
