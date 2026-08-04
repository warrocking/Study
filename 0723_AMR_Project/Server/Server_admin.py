# Server_admin.py (구 TestServer_admin.py)
#
# 총괄(관리자) 노트북에서 실행하는 서버 - 제가 직접 실행하는 파일입니다.
# 중계기(Server_Connector.py, 또는 각 로봇용 NabbVNN.py)를 여러 대 동시에 받을
# 수 있습니다 - 기계가 늘어나도 이 파일은 그대로 두고 각 중계기 쪽 RELAY_NAME만
# 새로 정해서 실행하면 자동으로 접속 목록에 추가됩니다.
#
# 접속을 계속 받아주는 부분은 별도 스레드(accept_loop)로 돌리고, 메인 스레드는
# 관리자가 입력하는 명령을 처리합니다 - 이 둘은 동시에 일어나야 해서 스레드가
# 실제로 필요한 경우입니다.
#
# 명령 입력 형식: "이름 명령" (예: "5abb Start"), 전체에게는 "all 명령".
# 종료는 "/quit".
#
# 실행 (VSCode 통합 터미널, PowerShell, cmd.exe 어디서든 동일하게 동작):
#     python Server_admin.py
#
# ===== 터미널 UI/UX 관련 (5abb 커넥터 V04와 같은 원리) =====
#   - Windows 콘솔 코드페이지/ANSI 색상 모드를 직접 설정 - 어떤 터미널
#     (cmd.exe/PowerShell/Windows Terminal/VSCode 등)에서 실행해도 한글이
#     깨지거나 크래시 나지 않고, 색상도 최대한 나오게 함 (지원 안 되면
#     색상만 자동으로 끔).
#   - 접속/끊김/명령 전송 이벤트마다 시간과 색상을 붙여서 지금 무슨 일이
#     일어났는지 스크롤만으로 바로 파악되게 함.
#   - 예상하지 못한 에러가 나도 창이 바로 닫히지 않고 원인을 보여준 뒤
#     Enter를 눌러야 닫히게 함 (더블클릭 실행 대비).

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
# 5abb 커넥터(NabbVNN.py, V04)에서 검증한 것과 동일한 설정. 실행 환경에 상관없이
# 항상 같은 방식으로 동작하도록 시작 시점에 콘솔을 직접 맞춘다.

def _enable_windows_console_support():
    """Windows 콘솔에서 UTF-8 출력과 ANSI 색상이 최대한 잘 나오도록 시도한다.
    실패해도 예외를 던지지 않고 성공 여부만 반환한다 - 실패하면 아래에서
    색상 사용을 그냥 꺼버리는 판단 근거로만 쓴다."""
    if sys.platform != "win32":
        return True   # Windows가 아니면(리눅스/맥 터미널) 기본이 대부분 UTF-8 + ANSI 지원

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


class C:
    RESET = "\033[0m" if USE_COLOR else ""
    BOLD = "\033[1m" if USE_COLOR else ""
    DIM = "\033[2m" if USE_COLOR else ""
    RED = "\033[91m" if USE_COLOR else ""
    GREEN = "\033[92m" if USE_COLOR else ""
    YELLOW = "\033[93m" if USE_COLOR else ""
    CYAN = "\033[96m" if USE_COLOR else ""
    MAGENTA = "\033[95m" if USE_COLOR else ""


# 이모지/박스 문자는 글꼴에 그림이 없어 네모로 깨질 수 있어서 안 쓰고,
# 어디서나 보이는 일반 문자만 사용한다.
TAG_OK = "[연결됨]"
TAG_ERR = "[끊김]"
TAG_INFO = "[안내]"
TAG_SEND = "[전송]"
TAG_DONE = "[작업완료]"

# 로봇(ABB)이 작업 사이클을 다 마치고 커넥터를 통해 보내는 완료 신호의 키워드.
# 커넥터가 "ABB: Done" 형태로 전달해준다 - 3abb_V07.mod/5abb_V09.mod의
# SocketSend srv_client_socket \Str:="Done"; 과 짝을 이룬다.
DONE_KEYWORD = "done"


def now():
    return datetime.now().strftime("%H:%M:%S")


def print_banner():
    print(f"{C.BOLD}{C.CYAN}")
    print("=========================================")
    print("   관리자 서버를 시작합니다")
    print("=========================================")
    print(C.RESET)
    if not USE_COLOR:
        print(f"{TAG_INFO} 이 콘솔에서는 색상을 못 켰습니다 - 색상 없이 진행합니다.\n")
    print(f"{C.DIM}명령 입력 형식: '이름 명령' (예: '5abb Start') / 전체: 'all 명령' / 종료: '/quit'{C.RESET}\n")


def send_text(connection, text):
    connection.sendall((text + "\n").encode(ENCODING))


def receive_text(reader):
    line = reader.readline()
    if line == "":
        return None
    return line.rstrip("\r\n")


def accept_loop(server_socket):
    """새 중계기 접속을 계속 받아서 이름별로 등록하는 백그라운드 스레드.

    accept()를 무한정 블로킹하지 않도록 1초 타임아웃을 두고, 그때마다
    stop_event를 확인함 - Ctrl+C 이후 프로그램이 이 스레드 때문에 계속
    떠 있는 상태를 막기 위함.

    accept() 직후 "이름 받기"는 이 스레드에서 바로 처리하지 않고 별도
    스레드(register_connection)에 넘긴다 - 여러 중계기가 거의 동시에
    접속할 때, 한 중계기의 이름 수신이 조금 늦어져도 그 뒤에 대기 중인
    다른 접속들이 accept() 자체를 못 받는 일이 없도록 하기 위함이다."""
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
    """새로 accept된 연결 하나의 등록을 전담하는 스레드.

    이름을 5초 안에 못 받으면 포기하고 연결을 닫는다 - 이름을 안 보내는
    깨진 접속 하나 때문에 스레드가 무한정 남아있는 것을 막기 위함.
    등록에 성공하면 이 스레드가 그대로 read_status_loop로 이어받는다."""
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

    print(f"\n{C.GREEN}{TAG_OK} [{now()}] {name} 연결됨: {address}{C.RESET}")
    read_status_loop(name, connection, reader)


def read_status_loop(name, connection, reader):
    """등록 이후 그 중계기가 보내는 상태 메시지(예: ABB 연결 끊김/재연결,
    작업 완료 신호)를 계속 읽어서 출력하는 스레드. 작업 완료 신호는 다른
    상태 메시지들과 섞이지 않도록 굵은 초록색으로 따로 강조한다 - 연결
    끊김/재연결 같은 잡다한 상태 로그 사이에서도 바로 눈에 띄어야 하기
    때문이다. 연결이 끊기면 목록에서도 제거한다."""
    try:
        while True:
            message = receive_text(reader)
            if message is None:
                break

            if DONE_KEYWORD in message.lower():
                print(f"\n{C.BOLD}{C.GREEN}{TAG_DONE} [{now()}] {name} 작업 완료!{C.RESET} "
                      f"{C.DIM}({message}){C.RESET}")
            else:
                print(f"\n{C.CYAN}[{now()}] {name} 상태:{C.RESET} {message}")
    except OSError:
        pass
    finally:
        with connections_lock:
            if connections.get(name) is connection:
                connections.pop(name, None)
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
    server_socket.settimeout(1.0)   # accept()가 1초마다 깨어나서 stop_event를 확인하게 함

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
        stop_event.set()   # accept_loop에게 종료를 알림 (다음 타임아웃 때 확인함)
        with connections_lock:
            for connection in connections.values():
                connection.close()
            connections.clear()
        server_socket.close()


if __name__ == "__main__":
    print_banner()

    try:
        run_admin_server(HOST, PORT)
    except KeyboardInterrupt:
        print()
        print(f"{C.YELLOW}Ctrl+C가 눌려서 관리자 서버를 종료합니다.{C.RESET}")
    except Exception:
        # 예상하지 못한 에러도 원인을 보여준 뒤 창이 바로 닫히지 않게 한다 -
        # 더블클릭으로 실행했을 때 에러가 뜨자마자 창이 사라지는 것을 막기 위함.
        print()
        print(f"{C.RED}{TAG_ERR} 예상하지 못한 오류가 발생했습니다:{C.RESET}")
        print(f"{C.RED}{traceback.format_exc()}{C.RESET}")
        try:
            input("확인했으면 Enter를 눌러 창을 닫으세요...")
        except (EOFError, KeyboardInterrupt):
            pass
