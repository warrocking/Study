# Server_admin_V3.py (Server_admin_V2.py 기반)
#
# 총괄(관리자) 노트북에서 실행하는 서버 - 제가 직접 실행하는 파일입니다.
#
# V2와의 차이 (자동 생산 오케스트레이션 추가):
#   지금까지는 관리자가 "이름 명령"을 하나씩 직접 입력해야만 로봇이 움직였다.
#   이 버전은 팀장님 PPT(8번 슬라이드)의 정해진 순서 -
#     3abb·5abb 동시 Start -> 3abb 완료 대기 -> AMR을 3(픽업)->4(하차)->3(빈
#     파렛트 반납) 순서로 이동 -> 5abb 완료 대기(3번 처리하는 동안 이미
#     끝났으면 즉시 통과) -> AMR을 5->4->5 순서로 이동 -> 다음 차량 반복
#   을 자동으로 수행하는 "오케스트레이터"를 백그라운드 스레드로 추가했다.
#   관리자는 "produce 2" 한 번만 입력하면 차 2대가 끝날 때까지 알아서
#   진행된다. 기존처럼 "이름 명령"으로 개별 조작하는 것도 그대로 되므로,
#   오케스트레이터가 예상과 다르게 움직이면 언제든 수동으로 끼어들 수 있다.
#
#   ===== 아직 정해지지 않아서 자리만 잡아둔 부분 (실제 값으로 바꿔야 함) =====
#   1) AMR_COMMANDS - "3번으로 가라"/"4번에 내려놔라" 등에 대응하는 실제 AMR
#      매크로/루트 명령 이름이 아직 없다고 하셔서, 지금은 자리만 잡아둔
#      이름(GotoUpperPickup 등)을 그대로 amr에게 보낸다. 실제 명령 체계가
#      정해지면 이 딕셔너리 값만 바꾸면 된다 - 나머지 로직은 안 건드려도 됨.
#   2) ARRIVED_KEYWORD - AMR이 "도착했다"고 알릴 때 어떤 문자열을 보낼지도
#      아직 안 정해졌다고 하셔서, amr이 보내는 메시지에 "arrived"라는 단어가
#      들어있으면 도착으로 인식하도록 임시로 정했다. Arduino 쪽에서 이
#      단어를 포함해서 보내도록 맞추거나, 실제 형식이 정해지면 아래
#      is_arrival_message() 함수만 고치면 된다.
#   두 가지 다 실제 값이 정해지기 전까지는 오케스트레이터가 AMR 응답을
#   무한정 기다리게 되니(타임아웃 없음 - 의도적으로 넣지 않음, 아래 이유
#   참고), "produce" 실행 중 AMR이 실제로 안 움직이는 게 정상입니다.
#
# 나머지는 V2와 동일:
#   - 상태판(HEARTBEAT/STATUS는 로그에 안 찍고 화면 위 고정 패널만 갱신)
#   - Windows 콘솔 UTF-8/색상 자동 설정, 크래시 시 창 안 닫힘
#   - 명령 입력 형식: "이름 명령" (예: "5abb Start"), 전체는 "all 명령", 종료는 "/quit"
#
# 실행 (VSCode 통합 터미널, PowerShell, cmd.exe 어디서든 동일하게 동작):
#     python Server_admin_V3.py
#
# 새 명령:
#     produce <대수>   예: "produce 2" - 지정한 대수만큼 3->4->3->5->4->5
#                       순서를 자동 반복. 이미 진행 중이면 무시하고 안내만 함.
#     produce stop      진행 중인 오케스트레이터를 다음 단계 경계에서 멈춤
#                       (즉시 정지 아님 - 진짜 비상정지는 로봇 자체의 안전
#                       장치를 쓸 것. 아래 stop_requested 설명 참고).

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
TAG_ARRIVED = "[도착]"
TAG_ORCH = "[생산진행]"

DONE_KEYWORD = "done"
# TODO(2): 실제 AMR 도착 신호 형식이 정해지면 이 단어/판정 방식을 바꿀 것.
ARRIVED_KEYWORD = "arrived"

KNOWN_RELAYS = ["3abb", "4abb", "5abb", "amr"]
EXTRA_SLOTS = 3

ROUTINE_PREFIXES = ("heartbeat", "status")

# TODO(1): 실제 AMR 매크로/루트 명령 이름이 정해지면 오른쪽 문자열만 교체할 것.
# 왼쪽 키는 오케스트레이터 코드에서 참조하는 이름이라 그대로 두면 된다.
AMR_COMMANDS = {
    "goto_3_pickup": "GotoUpperPickup",     # 3abb에서 완성 상부 픽업
    "goto_4_drop_upper": "GotoDropoffUpper",  # 4abb에 상부 하차
    "goto_3_return": "GotoUpperReturn",     # 3abb로 빈 파렛트 반납
    "goto_5_pickup": "GotoLowerPickup",     # 5abb에서 완성 하부 픽업
    "goto_4_drop_lower": "GotoDropoffLower",  # 4abb에 하부 하차
    "goto_5_return": "GotoLowerReturn",     # 5abb로 빈 파렛트 반납
}

# 오케스트레이터가 3abb/5abb의 완료 신호, amr의 도착 신호를 기다릴 때 쓰는
# 신호기(threading.Event) - 큐 대신 이걸 쓰는 이유: "3abb 처리 중에 5abb가
# 먼저 끝나버리는" 경우에도, 이벤트는 그냥 켜진 채로 남아있다가 나중에
# wait()하면 즉시 통과되므로 순서가 꼬여도 신호를 놓치지 않는다(큐였다면
# 엉뚱한 대기 지점에서 꺼내져 버려질 위험이 있음).
done_events = {"3abb": threading.Event(), "5abb": threading.Event()}
amr_arrived_event = threading.Event()

orchestrator_lock = threading.Lock()
orchestrator_thread = None
stop_requested = threading.Event()   # "produce stop" 요청 - 다음 단계 경계에서만 확인함(즉시 정지 아님)


def now():
    return datetime.now().strftime("%H:%M:%S")


def is_routine_status(message):
    lowered = message.strip().lower()
    return lowered.startswith(ROUTINE_PREFIXES)


def is_arrival_message(name, message):
    return name == "amr" and ARRIVED_KEYWORD in message.lower()


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
    밀리지 않게 한다."""

    def __init__(self, known_names, extra_slots):
        self.lock = threading.Lock()
        self.slots = list(known_names)
        self.extra_slots = extra_slots
        self.extra_names = []
        self.header_lines = 2
        self.panel_rows = len(self.slots) + self.extra_slots
        self.footer_lines = 1
        self.top_reserved = self.header_lines + self.panel_rows + self.footer_lines
        self.cols, _ = _terminal_size()

    def setup(self):
        if not USE_DASHBOARD:
            return
        cols, rows = _terminal_size()
        self.cols = cols
        sys.stdout.write("\033[2J\033[H")

        sys.stdout.write(f"{C.BOLD}{C.CYAN}관리자 서버 - 연결 현황{C.RESET}\n\n")
        for name in self.slots:
            self._write_row_text(name, "대기 중입니다...", C.DIM)
        for i in range(self.extra_slots):
            sys.stdout.write("\n")
        sys.stdout.write(f"{C.DIM}{'-' * min(60, cols)}{C.RESET}\n")

        sys.stdout.write(f"\033[{self.top_reserved + 1};{rows}r")
        sys.stdout.write(f"\033[{self.top_reserved + 1};1H")
        sys.stdout.flush()

    def _row_index_for(self, name):
        if name in self.slots:
            return self.slots.index(name)
        if name not in self.extra_names:
            if len(self.extra_names) >= self.extra_slots:
                return None
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
              f"자동생산: 'produce 2' / 종료: '/quit'{C.RESET}\n")
        return

    print(f"{C.BOLD}{C.CYAN}")
    print("=========================================")
    print("   관리자 서버를 시작합니다")
    print("=========================================")
    print(C.RESET)
    if not USE_COLOR:
        print(f"{TAG_INFO} 이 콘솔에서는 색상을 못 켰습니다 - 색상 없이 진행합니다.\n")
    print(f"{C.DIM}명령 입력 형식: '이름 명령' (예: '5abb Start') / 전체: 'all 명령' / "
          f"자동생산: 'produce 2' / 종료: '/quit'{C.RESET}\n")


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

    HEARTBEAT/STATUS는 상태판만 갱신하고 로그에는 안 남긴다. 3abb/5abb의
    작업완료 신호와 amr의 도착 신호는 오케스트레이터가 기다리는
    이벤트이므로, 화면 표시와 별개로 반드시 여기서 해당 Event를 set()
    해줘야 한다 - 오케스트레이터는 이 이벤트 외에는 상태 메시지를 직접
    읽지 않는다."""
    try:
        while True:
            message = receive_text(reader)
            if message is None:
                break

            lowered = message.lower()

            if DONE_KEYWORD in lowered and name in done_events:
                done_events[name].set()
                dashboard.update(name, f"{now()}  {message}", C.BOLD + C.GREEN)
                print(f"\n{C.BOLD}{C.GREEN}{TAG_DONE} [{now()}] {name} 작업 완료!{C.RESET} "
                      f"{C.DIM}({message}){C.RESET}")
            elif is_arrival_message(name, message):
                amr_arrived_event.set()
                dashboard.update(name, f"{now()}  {message}", C.BOLD + C.GREEN)
                print(f"\n{C.BOLD}{C.GREEN}{TAG_ARRIVED} [{now()}] {name} 도착!{C.RESET} "
                      f"{C.DIM}({message}){C.RESET}")
            elif is_routine_status(message):
                dashboard.update(name, f"{now()}  {message}", C.CYAN)
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


# ===== 자동 생산 오케스트레이터 =====

def orch_log(text, color=C.CYAN):
    print(f"\n{color}{TAG_ORCH} [{now()}] {text}{C.RESET}")


def run_amr_leg(step_name, command_key):
    """AMR에게 명령 하나를 보내고 도착 신호를 기다린다. 'produce stop'이
    요청되면 이 단계가 끝나는 시점(도착 신호를 받은 직후)에 멈춘다."""
    orch_log(f"AMR -> {step_name}")
    amr_arrived_event.clear()
    send_to("amr", AMR_COMMANDS[command_key])
    amr_arrived_event.wait()   # TODO(2)가 해결되기 전까지는 무한 대기 - 의도된 동작
    orch_log(f"AMR {step_name} 도착 확인")


def run_production(car_count):
    """PPT 8번 슬라이드의 고정 순서(3 항상 먼저 -> 5)를 car_count대만큼
    반복한다. 상세 순서:
      1) 3abb, 5abb에 동시에 Start
      2) 3abb 완료 대기 -> AMR: 3(픽업)->4(하차)->3(빈 파렛트 반납)
      3) 5abb 완료 대기(이미 끝났으면 즉시 통과) -> AMR: 5->4->5
      4) 다음 차량 반복

    done_events/amr_arrived_event를 큐가 아니라 Event로 쓰는 이유는 위쪽
    주석 참고 - 순서가 뒤바뀌어도 신호를 잃어버리지 않기 위함이다."""
    orch_log(f"자동 생산 시작 - 목표 {car_count}대", C.BOLD + C.CYAN)

    for car_index in range(1, car_count + 1):
        if stop_requested.is_set():
            orch_log("정지 요청으로 다음 차량 시작 전에 멈춥니다.", C.YELLOW)
            break

        orch_log(f"{car_index}/{car_count}번째 차량 - 3abb·5abb 동시 시작", C.BOLD + C.CYAN)
        done_events["3abb"].clear()
        done_events["5abb"].clear()
        send_to("3abb", "Start")
        send_to("5abb", "Start")

        done_events["3abb"].wait()
        orch_log("3abb 작업 완료 확인 - 상부 이송 시작")
        run_amr_leg("3abb 픽업", "goto_3_pickup")
        run_amr_leg("4abb 상부 하차", "goto_4_drop_upper")
        run_amr_leg("3abb 빈 파렛트 반납", "goto_3_return")

        if stop_requested.is_set():
            orch_log("정지 요청으로 하부 이송 전에 멈춥니다.", C.YELLOW)
            break

        done_events["5abb"].wait()   # 위 3단계 처리 중 이미 끝났으면 즉시 통과
        orch_log("5abb 작업 완료 확인 - 하부 이송 시작")
        run_amr_leg("5abb 픽업", "goto_5_pickup")
        run_amr_leg("4abb 하부 하차", "goto_4_drop_lower")
        run_amr_leg("5abb 빈 파렛트 반납", "goto_5_return")

        orch_log(f"{car_index}/{car_count}번째 차량 완료!", C.BOLD + C.GREEN)

    orch_log("자동 생산 종료", C.BOLD + C.CYAN)
    with orchestrator_lock:
        global orchestrator_thread
        orchestrator_thread = None
        stop_requested.clear()


def handle_produce_command(argument):
    """'produce <대수>' 또는 'produce stop' 입력을 처리한다."""
    global orchestrator_thread

    argument = argument.strip().lower()

    if argument == "stop":
        with orchestrator_lock:
            if orchestrator_thread is None:
                print(f"{C.YELLOW}{TAG_INFO} 지금 진행 중인 자동 생산이 없습니다.{C.RESET}")
                return
            stop_requested.set()
        print(f"{C.YELLOW}{TAG_INFO} 정지를 요청했습니다 - 지금 진행 중인 단계가 끝나면 멈춥니다 "
              f"(즉시 정지가 아닙니다 - 비상정지는 로봇 자체 안전장치를 쓰세요).{C.RESET}")
        return

    try:
        car_count = int(argument)
        if car_count <= 0:
            raise ValueError
    except ValueError:
        print(f"{C.YELLOW}형식: 'produce 2' (숫자만큼 자동 생산) 또는 'produce stop'{C.RESET}")
        return

    with orchestrator_lock:
        if orchestrator_thread is not None:
            print(f"{C.YELLOW}{TAG_INFO} 이미 자동 생산이 진행 중입니다 - "
                  f"멈추려면 'produce stop'을 입력하세요.{C.RESET}")
            return
        stop_requested.clear()
        orchestrator_thread = threading.Thread(
            target=run_production, args=(car_count,), daemon=True
        )
        orchestrator_thread.start()


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
                print(f"{C.YELLOW}형식: '이름 명령' (예: '5abb Start') / 'all 명령' / "
                      f"'produce 2'{C.RESET}")
                continue

            name, command = parts

            if name.lower() == "produce":
                handle_produce_command(command)
                continue

            send_to(name, command)
    finally:
        stop_event.set()
        stop_requested.set()
        with connections_lock:
            for connection in connections.values():
                connection.close()
            connections.clear()
        server_socket.close()
        if USE_DASHBOARD:
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
