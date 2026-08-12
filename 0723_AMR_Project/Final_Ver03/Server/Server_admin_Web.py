#!/usr/bin/env python3
"""Server_admin_Web.py - Final_Ver03

0723_AMR_Project/Final_Ver03/ 폴더는 Rapid/·Server/ 폴더에 흩어져 있던
버전 파일들(Server_admin_Web_ver04.py, 3abb_V13.mod, 4abb_V07.mod,
5abb_V16.mod, 3abb_V04.py, 4abb_V04.py, 5abb_V06.py) 중 "현재 기준으로
실제로 맞물려 돌아가는 최신 세트"를 한 군데에 모아둔 것입니다. AMR.ino는
아두이노 담당자가 만든 실제 펌웨어(V16,
AMR_Server_Bridge_V16_ARDUINO_CONVEYOR_AUTO_2_CYCLES)를 그대로 복사해 둔
참고용 사본이며, 이 서버는 그 코드를 전혀 수정하지 않고 대상으로 삼습니다.

Server_admin_Web_ver03.py 대비 이 버전에서 바뀐 것 - AMR과의 통신을 실제
펌웨어(AMR.ino V16) 프로토콜에 맞게 전면 재작성하고, 출고 컨베이어를 AMR
도착 확인 후로 게이팅합니다:

  ver03까지는 "RUN ROUTE_ST1 FWD" 같은 개별 이동 명령과 "arrived" 키워드
  매칭으로 AMR을 다리(leg)별로 직접 조종하려 했는데(AMR_COMMANDS/
  _run_amr_leg), 실제 AMR.ino V16 펌웨어는 그런 명령을 아예 모릅니다
  ("RUN ..."을 받으면 "STATUS RUN_IGNORED"로 무시). 이 버전은 그 로직을
  전부 걷어내고, 펌웨어가 실제로 지원하는 프로토콜로 다시 짰습니다.

핵심 아이디어 - "AMR 펌웨어를 고치지 않고도, AMR이 이미 보내고 있는 STATUS
로그를 서버가 읽어서 출고 컨베이어를 AMR 도착 조건에 건다":
  이 펌웨어는 admin 소켓에 "START" 명령 1회를 받으면 ST1->ST2->ST1->ST3->
  ST2->ST3 6단계 왕복을 자동으로 "2 cycles" 실행합니다(=3abb/5abb가 Start
  1회에 만드는 차량 2대와 1:1 대응). "RUN ..." 개별 이동 명령은 명시적으로
  무시하며("STATUS RUN_IGNORED"), 진행 상황은 ARCL의 WaitState/Pausing
  감지에 맞춰 그때그때 STATUS 로그로 그대로 보고합니다 - 서버는 이 로그를
  읽기만 하면 되고 펌웨어 코드는 전혀 바꾸지 않습니다.

  각 cycle의 6단계 중 3abb/5abb에서 실제로 "몸체를 실어 가는"(=그 스테이션의
  출고 컨베이어가 함께 돌아야 하는) 순간은 정확히 두 곳뿐입니다:
    - ST1 첫 방문(step 1, route="START" 또는 2번째 cycle은 "ROUTE_ST1"):
      AMR이 D2 센서로 물체를 감지할 때까지 FWD로 계속 당겨 싣는 동작
      -> "STATUS CONVEYOR_START direction=FWD mode=UNTIL_D2 ..." 로 보고됨
    - ST3 방문(step 4, route="ROUTE_ST3"): AMR이 FWD로 5초간 싣는 동작
      -> "STATUS CONVEYOR_START direction=FWD timer_ms=5000 step=4 ..." 로 보고됨
  (ST1의 두 번째 방문(step 3, REV)과 ST3의 두 번째 방문(step 6, REV)은
  AMR이 되돌아와 반납/하차하는 동작이라 3abb/5abb의 ReadyForPickup 핸드셰이크
  대상이 아닙니다 - 그래서 direction=FWD인 CONVEYOR_START만 골라서 씁니다.)

  그래서 3abb/5abb의 컨베이어를 AMR 도착 확인 후로 게이팅합니다 (RAPID:
  3abb.mod/5abb.mod에 ReadyForPickup -> WaitForAmrArrived -> ConveyDone
  대기가 들어있음). 서버 쪽은 ABB의 "ReadyForPickup"과 AMR의 위 STATUS
  CONVEYOR_START 로그라는 서로 다른 두 이벤트 스트림을 스테이션별로
  매칭하는 백그라운드 스레드(_run_pickup_matcher)가 담당합니다 - 어느
  쪽이 먼저 도착하든 큐에 쌓아 두고 매칭되는 즉시 그 스테이션에
  "AmrArrived"를 보냅니다.

  AMR 펌웨어 코드 변경은 전혀 필요 없습니다 - 이미 나오고 있던 STATUS 로그를
  서버가 더 이상 무시하지 않는 것뿐입니다.

실행:
    pip install flask   (최초 1회)
    python Server_admin_Web.py
    -> 브라우저에서 http://localhost:8080 접속
"""

from __future__ import annotations

import json
import queue
import socket
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime

try:
    from flask import Flask, Response, jsonify, render_template_string, request, stream_with_context
except ImportError:
    raise SystemExit(
        "Flask가 설치되어 있지 않습니다. 먼저 다음을 실행하세요:\n"
        "    pip install flask"
    )


HOST = "0.0.0.0"
PORT = 5000            # 로봇/AMR 중계기가 접속하는 TCP 포트 (기존과 동일)
WEB_PORT = 8080         # 사람이 브라우저로 접속하는 포트
ENCODING = "utf-8"
BROADCAST_NAME = "all"
DONE_KEYWORD = "done"
START_COMMAND = "Start"
FOUR_ABB_NAME = "4abb"

KNOWN_RELAYS = ["3abb", "4abb", "5abb", "amr"]

# AMR(Arduino, AMR.ino V16)은 admin 소켓으로 "START" 명령 1회를 받으면
# ST1->ST2->ST1->ST3->ST2->ST3 6단계 왕복을 자동으로 2 cycle(=차량 2대분)
# 실행하는 자율 장비다. "RUN ..." 개별 이동 명령은 명시적으로 무시한다
# ("STATUS RUN_IGNORED"). 진행 상황은 STATUS 로그로 실시간 보고되며,
# Ver02는 그중 "STATUS CONVEYOR_START direction=FWD ..." 로그만 골라
# 출고 컨베이어 게이팅에 쓴다 (아래 AMR_CONVEYOR_START_KEYWORD 참고).
AMR_START_COMMAND = "START"
# 두 번째 이상 생산 실행 전, AMR의 내부 step/cycle 카운터를 처음(ST1)으로
# 되돌리기 위한 명령. 펌웨어가 이미 지원한다 (RESET_SEQUENCE 핸들러 참고).
AMR_RESET_COMMAND = "RESET_SEQUENCE"

# 출고 컨베이어를 AMR 도착 조건에 걸기 위한 신호. 3abb/5abb 둘 다 씀.
# - ABB -> 서버: 조립 끝내고 출고 위치에 놨으니 픽업 대기 중
READY_KEYWORD = "readyforpickup"
# - ABB -> 서버: (AmrArrived를 받고) 실제로 출고 컨베이어를 구동했음
CONVEY_DONE_KEYWORD = "conveydone"
# - 서버 -> ABB: AMR이 이 스테이션 출고 컨베이어에 도착했으니 이제 컨베이어를 돌려도 됨
AMR_ARRIVED_COMMAND = "AmrArrived"
# - amr -> 서버: 펌웨어가 AMR 자신의 컨베이어를 실제로 구동하기 시작할 때 보내는
#   로그("STATUS CONVEYOR_START direction=FWD ..."). direction=FWD만 "몸체를
#   실어 간다"는 뜻이고 direction=REV는 반납/하차 동작이라 대상이 아니다.
AMR_CONVEYOR_START_KEYWORD = "conveyor_start direction=fwd"

# 이 두 스테이션만 "픽업 대기 <-> AMR 도착 확인 -> 컨베이어 허가" 흐름을 탄다.
PICKUP_STATIONS = ("3abb", "5abb")

# AMR_CONVEYOR_START_KEYWORD 로그 한 줄만으로는 ST1/ST3 어느 쪽인지 알 수
# 없으므로(둘 다 direction=FWD), 펌웨어가 그 줄에 같이 붙여 보내는 세부
# 태그로 구분한다: ST1 첫 방문(ACTION_LOAD_UNTIL_D2)만 "mode=UNTIL_D2"를
# 붙이고, ST3 방문(ACTION_LOAD_FWD_5S)만 "step=4"를 붙인다 (AMR.ino의
# startLoadUntilD2()/startDockAction() 참고). 순서대로 검사해서 먼저
# 매칭되는 스테이션으로 확정한다.
AMR_CONVEYOR_START_TAG_TO_PICKUP_STATION = (
    ("mode=until_d2", "3abb"),
    ("step=4", "5abb"),
)

# ----- AMR 서버 자동 탐색(UDP) -----
UDP_PORT = 5001
DISCOVERY_REQUEST = "AMR_SERVER_DISCOVER_V1 device=amr"
DISCOVERY_RESPONSE = f"AMR_SERVER_V1 name=admin tcp_port={PORT}"
DISCOVERY_MAX_PACKET_BYTES = 512
DISCOVERY_LOG_INTERVAL_SECONDS = 60   # 같은 주소는 이 시간 안에 재발견해도 로그를 다시 남기지 않음


def now() -> str:
    return datetime.now().strftime("%H:%M:%S")


def is_routine_status(message: str) -> bool:
    return message.strip().lower().startswith(("heartbeat", "status"))


@dataclass
class Relay:
    name: str
    sock: socket.socket
    address: tuple[str, int]
    lock: threading.Lock = field(default_factory=threading.Lock)


class Broadcaster:
    """queue.Queue와 같은 .put() 인터페이스를 갖되, 붙어있는 모든 구독자
    (브라우저 탭 하나당 SSE 연결 하나)에게 이벤트를 그대로 복사해서 보낸다."""

    def __init__(self) -> None:
        self._subscribers: list[queue.Queue] = []
        self._lock = threading.Lock()

    def put(self, item: dict) -> None:
        with self._lock:
            subscribers = list(self._subscribers)
        for subscriber_queue in subscribers:
            subscriber_queue.put(item)

    def subscribe(self) -> "queue.Queue":
        subscriber_queue: "queue.Queue" = queue.Queue()
        with self._lock:
            self._subscribers.append(subscriber_queue)
        return subscriber_queue

    def unsubscribe(self, subscriber_queue: "queue.Queue") -> None:
        with self._lock:
            if subscriber_queue in self._subscribers:
                self._subscribers.remove(subscriber_queue)


class AdminServer:
    """네트워킹 + 자동 생산 오케스트레이션 + AMR UDP 자동 탐색 응답 + 4abb
    Start-once 관리. 화면(Flask/브라우저)은 전혀 모른다 - 전부
    event_queue(Broadcaster)로만 알린다."""

    def __init__(self, event_queue: "Broadcaster"):
        self.events = event_queue
        self.relays: dict[str, Relay] = {}
        self.relays_lock = threading.Lock()
        self.running = threading.Event()
        self.server_socket: socket.socket | None = None
        self.udp_socket: socket.socket | None = None

        self.done_events = {"3abb": threading.Event(), "5abb": threading.Event()}
        self.orchestrator_thread: threading.Thread | None = None
        self.stop_requested = threading.Event()

        # 출고 컨베이어를 AMR 도착 조건에 거는 데 쓰는 상태. ready_queues는
        # ABB의 "ReadyForPickup"(스테이션당 Start 1회에 2번), arrived_queues는
        # AMR의 "EVENT DOCK_WAIT_STARTED station=..."을 파싱한 결과를 담는다.
        # 둘 다 Queue인 이유는 두 이벤트 스트림이 서로 독립적으로, 어느 쪽이
        # 먼저 도착할지 모르는 채로 들어오기 때문 - 매칭 스레드
        # (_run_pickup_matcher)가 두 큐에서 하나씩 꺼내 짝을 맞춘다.
        self.ready_queues = {name: queue.Queue() for name in PICKUP_STATIONS}
        self.amr_arrived_queues = {name: queue.Queue() for name in PICKUP_STATIONS}
        self.convey_done_events = {name: threading.Event() for name in PICKUP_STATIONS}

        # 브라우저가 새로고침하거나 새 탭을 열 때 SSE로 지나간 과거 이벤트를
        # 놓쳐도 바로 채워 넣을 수 있도록 최근 상태를 기억해 둔다.
        self.state_lock = threading.Lock()
        self.relay_status: dict[str, dict] = {}
        self.log_history: deque = deque(maxlen=300)
        self.orchestrator_running = False

        # 같은 Arduino 주소의 탐색 요청 로그를 너무 자주 남기지 않기 위한 기록.
        self._discovery_lock = threading.Lock()
        self._discovery_last_logged: dict[str, float] = {}

        # 4abb는 Start를 한 번 받으면 계속 PLC 센서를 감시하는 무한 대기
        # 상태로 들어간다. 이 서버가 켜져 있는 동안 이미 Start를 보냈으면
        # 다시 보내지 않기 위한 상태 - "물리적으로 4abb가 그 상태다"라는
        # 확인이 아니라 "이 서버가 Start 전송에 성공했다"는 기록일 뿐이다.
        self._four_abb_state_lock = threading.Lock()
        self._four_abb_start_sent = False

    # ----- 화면에 보낼 이벤트 (+ 스냅샷용 상태 기억) -----
    def log(self, message: str, tag: str = "info") -> None:
        entry = {"kind": "log", "time": now(), "message": message, "tag": tag}
        with self.state_lock:
            self.log_history.append(entry)
        self.events.put(entry)

    def set_relay_status(self, name: str, text: str, tag: str) -> None:
        entry = {"kind": "relay_status", "name": name, "text": text, "tag": tag}
        with self.state_lock:
            self.relay_status[name] = {"text": text, "tag": tag}
        self.events.put(entry)

    def set_orchestrator_state(self, running: bool) -> None:
        with self.state_lock:
            self.orchestrator_running = running
        self.events.put({"kind": "orch_state", "running": running})

    def snapshot(self) -> dict:
        with self.relays_lock:
            connected = sorted(self.relays.keys())
        with self.state_lock:
            return {
                "known_relays": KNOWN_RELAYS,
                "connected": connected,
                "relay_status": dict(self.relay_status),
                "log_history": list(self.log_history),
                "orchestrator_running": self.orchestrator_running,
                "admin_port": PORT,
                # 물리적 동작 확인이 아니라 "Start 전송 기록"일 뿐임에 유의.
                "four_abb_receiving_started": self._is_4abb_started(),
            }

    # ----- 4abb Start-once 상태 -----
    def _mark_4abb_started(self) -> None:
        with self._four_abb_state_lock:
            self._four_abb_start_sent = True

    def _is_4abb_started(self) -> bool:
        with self._four_abb_state_lock:
            return self._four_abb_start_sent

    # ----- 서버 -----
    def start(self) -> None:
        self.running.set()
        threading.Thread(target=self._serve, daemon=True).start()
        threading.Thread(target=self._serve_discovery, daemon=True).start()
        for station in PICKUP_STATIONS:
            threading.Thread(
                target=self._run_pickup_matcher, args=(station,), daemon=True
            ).start()

    def _run_pickup_matcher(self, station: str) -> None:
        """ready_queues[station](ABB의 ReadyForPickup)와
        amr_arrived_queues[station](AMR의 DOCK_WAIT_STARTED)를 계속
        지켜보다가 둘 다 준비되면 그 스테이션에 AmrArrived를 보내고
        ConveyDone까지 기다린다. 두 이벤트가 어느 순서로 오든(둘 다 큐라서
        먼저 온 쪽은 그냥 쌓여서 기다림) 상관없이 매칭한다. 생산 자동화
        여부와 무관하게 서버가 켜져 있는 동안 항상 돌아간다."""
        while self.running.is_set():
            try:
                self.ready_queues[station].get(timeout=1.0)
            except queue.Empty:
                continue

            self.log(f"{station} 픽업 대기 중 (ReadyForPickup) - AMR 도착 확인 대기", "orch")
            while self.running.is_set():
                try:
                    self.amr_arrived_queues[station].get(timeout=1.0)
                    break
                except queue.Empty:
                    continue
            if not self.running.is_set():
                return

            self.convey_done_events[station].clear()
            self.send(station, AMR_ARRIVED_COMMAND)
            self.log(f"{station} -> AmrArrived 전달, 출고 컨베이어 구동 대기 중", "orch")
            self.convey_done_events[station].wait()
            self.log(f"{station} 출고 컨베이어 구동 확인 (ConveyDone)", "orch")

    def _serve(self) -> None:
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((HOST, PORT))
            server.listen(10)
            server.settimeout(1.0)
            self.server_socket = server
            self.log(f"관리자 서버 시작됨: {HOST}:{PORT}", "ok")

            while self.running.is_set():
                try:
                    client, address = server.accept()
                except socket.timeout:
                    continue
                except OSError:
                    break
                threading.Thread(
                    target=self._handle_client, args=(client, address), daemon=True
                ).start()
        except OSError as exc:
            self.log(f"서버 오류: {exc}", "err")
        finally:
            self.running.clear()

    def _should_log_discovery(self, ip: str) -> bool:
        """같은 주소는 DISCOVERY_LOG_INTERVAL_SECONDS 안에 다시 봐도 로그를
        또 남기지 않는다. 최초 발견이거나 그 시간이 지난 뒤의 재발견만 True."""
        now_ts = time.monotonic()
        with self._discovery_lock:
            last = self._discovery_last_logged.get(ip)
            self._discovery_last_logged[ip] = now_ts
            if last is not None and (now_ts - last) < DISCOVERY_LOG_INTERVAL_SECONDS:
                return False
            return True

    def _serve_discovery(self) -> None:
        """Arduino가 보내는 UDP 탐색 요청에 응답한다 - 관리자 서버의 실제 IP를
        몰라도 Arduino가 이 노트북을 찾을 수 있게 해준다. TCP 서버(_serve)와는
        완전히 독립된 소켓/스레드라 서로 영향을 주지 않는다."""
        try:
            udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp.bind((HOST, UDP_PORT))
            udp.settimeout(1.0)
            self.udp_socket = udp
            self.log(f"AMR 탐색 응답 서버 시작됨: {HOST}:{UDP_PORT}", "ok")

            while self.running.is_set():
                try:
                    # 버퍼를 DISCOVERY_MAX_PACKET_BYTES보다 넉넉하게 잡는다 - Windows는
                    # 버퍼보다 큰 UDP 데이터그램이 오면(POSIX처럼 잘라서 주는 게 아니라)
                    # recvfrom 자체가 OSError(WSAEMSGSIZE)를 던지기 때문에, 살짝 큰
                    # 패킷까지는 일단 정상 수신한 뒤 아래에서 길이로 걸러낸다.
                    data, addr = udp.recvfrom(4096)
                except socket.timeout:
                    continue
                except OSError:
                    # 너무 큰 패킷 등으로 recvfrom 자체가 실패한 경우 - 소켓이 아직
                    # 살아있다면(정상 운영 중) 이 패킷만 무시하고 계속 수신한다.
                    # running이 꺼졌다면 stop()이 소켓을 닫아서 난 에러이므로 종료한다.
                    if self.running.is_set():
                        continue
                    break

                # 지나치게 긴 패킷은 무시
                if len(data) > DISCOVERY_MAX_PACKET_BYTES:
                    continue

                try:
                    message = data.decode(ENCODING, errors="strict").strip()
                except UnicodeDecodeError:
                    continue

                # 정확한 요청 문자열만 처리하고 나머지는 조용히 무시한다.
                if message != DISCOVERY_REQUEST:
                    continue

                should_log = self._should_log_discovery(addr[0])
                if should_log:
                    self.log(f"AMR discovery request: {addr[0]}", "info")

                try:
                    # 서버 IP를 직접 넣지 않는다 - Arduino는 이 UDP 응답 패킷의
                    # 발신 주소를 그대로 서버 IP로 사용한다 (sendto의 addr로
                    # 응답하면 OS가 올바른 로컬 인터페이스 주소를 채워준다).
                    udp.sendto(DISCOVERY_RESPONSE.encode(ENCODING), addr)
                except OSError as exc:
                    self.log(f"AMR 탐색 응답 전송 실패({addr[0]}): {exc}", "err")
                    continue

                if should_log:
                    self.log(f"AMR discovery response: tcp_port={PORT}", "info")
        except OSError as exc:
            if self.running.is_set():
                self.log(f"AMR 탐색 서버 오류: {exc}", "err")

    def _handle_client(self, client: socket.socket, address: tuple[str, int]) -> None:
        client.settimeout(5.0)
        name = ""
        reader = client.makefile("r", encoding=ENCODING, errors="replace", newline="\n")
        try:
            first_line = reader.readline(64)
            if not first_line:
                return
            name = first_line.strip()
            if not name or " " in name or len(name) > 40:
                self.log(f"알 수 없는 접속({address}) - 이름이 이상해서 닫습니다.", "warn")
                return

            client.settimeout(None)
            with self.relays_lock:
                old = self.relays.get(name)
                self.relays[name] = Relay(name, client, address)
            if old is not None:
                try:
                    old.sock.close()   # 같은 이름으로 재접속 - 이전 연결은 정리
                except OSError:
                    pass

            self.log(f"{name} 연결됨: {address[0]}:{address[1]}", "ok")
            self.set_relay_status(name, f"{now()}  연결됨", "ok")

            for line in reader:
                message = line.rstrip("\r\n")
                if not message:
                    continue
                self._handle_message(name, message)
        except (OSError, UnicodeError) as exc:
            if self.running.is_set():
                self.log(f"{name or address[0]} 연결 오류: {exc}", "err")
        finally:
            try:
                reader.close()
            except OSError:
                pass
            try:
                client.close()
            except OSError:
                pass
            if name:
                with self.relays_lock:
                    current = self.relays.get(name)
                    removed = current is not None and current.sock is client
                    if removed:
                        del self.relays[name]
                if removed:
                    self.log(f"{name} 연결이 끊겼습니다.", "err")
                    self.set_relay_status(name, f"{now()}  연결 끊김", "err")

    def _handle_message(self, name: str, message: str) -> None:
        lowered = message.lower()

        # "conveydone"에도 "done"이 부분 문자열로 들어있으므로, 아래의 일반
        # DONE_KEYWORD 체크보다 반드시 먼저 검사해야 한다.
        if READY_KEYWORD in lowered and name in self.ready_queues:
            self.ready_queues[name].put(message)
            self.log(f"{name} 출고 준비 완료 (ReadyForPickup): {message}", "orch")
            self.set_relay_status(name, f"{now()}  픽업 대기중", "cyan")
        elif CONVEY_DONE_KEYWORD in lowered and name in self.convey_done_events:
            self.convey_done_events[name].set()
            self.log(f"{name} 출고 컨베이어 구동 완료 (ConveyDone): {message}", "orch")
            self.set_relay_status(name, f"{now()}  컨베이어 구동 완료", "done")
        elif name == "amr" and AMR_CONVEYOR_START_KEYWORD in lowered:
            self._handle_amr_conveyor_start_event(message, lowered)
        elif DONE_KEYWORD in lowered and name in self.done_events:
            self.done_events[name].set()
            self.log(f"{name} 작업 완료! ({message})", "done")
            self.set_relay_status(name, f"{now()}  {message}", "done")
        elif is_routine_status(message):
            # HEARTBEAT/STATUS는 로그에 안 남기고 상태판만 갱신 (터미널/GUI판과 동일한 이유)
            self.set_relay_status(name, f"{now()}  {message}", "cyan")
        elif "err" in lowered:
            self.log(f"{name} 상태: {message}", "err")
            self.set_relay_status(name, f"{now()}  {message}", "err")
        else:
            self.log(f"{name} 상태: {message}", "cyan")
            self.set_relay_status(name, f"{now()}  {message}", "cyan")

    def _handle_amr_conveyor_start_event(self, message: str, lowered: str) -> None:
        """amr이 "STATUS CONVEYOR_START direction=FWD ..." 형태로 보내는 로그를
        같이 붙은 태그(mode=UNTIL_D2 -> 3abb, step=4 -> 5abb)로 매핑해서 해당
        픽업 스테이션의 amr_arrived_queues에 넣는다. direction=REV(반납/하차
        동작)는 애초에 이 핸들러까지 오지 않는다 - _handle_message에서
        AMR_CONVEYOR_START_KEYWORD("conveyor_start direction=fwd")로 이미
        걸러졌기 때문. 두 태그 중 어느 것도 없으면(원칙적으로는 발생하지
        않아야 함) 로그만 남기고 무시한다."""
        matched_station = None
        for tag, station in AMR_CONVEYOR_START_TAG_TO_PICKUP_STATION:
            if tag in lowered:
                matched_station = station
                break

        if matched_station is None:
            self.log(f"amr 컨베이어 구동 로그 (태그 불일치 - 무시): {message}", "warn")
            self.set_relay_status("amr", f"{now()}  {message}", "cyan")
            return

        self.amr_arrived_queues[matched_station].put(message)
        self.log(f"amr이 {matched_station} 출고 컨베이어에 도착 확인: {message}", "done")
        self.set_relay_status("amr", f"{now()}  {message}", "done")

    def send(self, name: str, command: str) -> tuple[bool, str]:
        command = command.strip()
        if not command:
            return False, "명령이 비어 있습니다."

        with self.relays_lock:
            if name.lower() == BROADCAST_NAME:
                targets = list(self.relays.values())
            elif name in self.relays:
                targets = [self.relays[name]]
            else:
                known = ", ".join(self.relays.keys()) if self.relays else "(없음)"
                return False, f"'{name}'은(는) 연결되어 있지 않습니다. 현재 접속: {known}"

        if not targets:
            return False, "연결된 중계기가 없습니다."

        ok_all = True
        for relay in targets:
            try:
                with relay.lock:
                    relay.sock.sendall((command + "\n").encode(ENCODING))
                self.log(f"{relay.name} -> {command}", "send")
            except OSError as exc:
                ok_all = False
                self.log(f"{relay.name} 전송 실패: {exc}", "err")
                with self.relays_lock:
                    self.relays.pop(relay.name, None)
                continue

            # 4abb에 Start가 실제로 성공적으로 나간 경우에만 기록한다 (수동
            # "4abb Start"든 "all Start"든 상관없이 - 이 대상이 4abb였고
            # 명령이 Start였고 전송이 성공했을 때만).
            if relay.name == FOUR_ABB_NAME and command.lower() == START_COMMAND.lower():
                self._mark_4abb_started()
                self.set_relay_status(
                    FOUR_ABB_NAME, f"{now()}  PLC 센서 감시·적재 대기 활성화", "ok"
                )

        return ok_all, ""

    # ----- 자동 생산 오케스트레이터 -----
    def _ensure_4abb_receiving(self) -> tuple[bool, str]:
        """자동 생산 전에 4abb의 무한 수신·적재 루프를 한 번만 시작한다."""
        with self.relays_lock:
            connected = FOUR_ABB_NAME in self.relays

        if not connected:
            return False, "4abb가 연결되어 있지 않아 자동 생산을 시작할 수 없습니다."

        if self._is_4abb_started():
            self.log(
                "4abb는 이미 PLC 센서 감시·적재 대기 상태로 간주합니다. Start를 다시 보내지 않습니다.",
                "orch",
            )
            return True, ""

        self.log("4abb에 Start 전송 - PLC 센서 감시·적재 무한 대기 활성화 요청", "orch")
        ok, error = self.send(FOUR_ABB_NAME, START_COMMAND)
        if not ok:
            return False, error or "4abb Start 전송에 실패했습니다."

        self.log("4abb Start 요청 전송 완료 - Done 응답은 기다리지 않습니다.", "orch")
        return True, ""

    def start_production(self) -> tuple[bool, str]:
        if self.orchestrator_thread is not None:
            return False, "이미 자동 생산이 진행 중입니다."
        self.stop_requested.clear()
        self.orchestrator_thread = threading.Thread(
            target=self._run_production, daemon=True
        )
        self.set_orchestrator_state(True)
        self.orchestrator_thread.start()
        return True, ""

    def request_stop_production(self) -> None:
        if self.orchestrator_thread is None:
            self.log("지금 진행 중인 자동 생산이 없습니다.", "warn")
            return
        self.stop_requested.set()
        self.log("정지를 요청했습니다 - 진행 중인 단계가 끝나면 멈춥니다 "
                  "(비상정지 아님, 로봇 자체 안전장치를 쓰세요).", "warn")

    def _run_production(self) -> None:
        # 4abb는 3abb/5abb처럼 매번 Start하는 장비가 아니다 - 생산 전체를
        # 통틀어 한 번만 Start해서 PLC 센서를 계속 감시하게 한다.
        ok, error = self._ensure_4abb_receiving()
        if not ok:
            self.log(f"자동 생산 시작 취소: {error}", "err")
            self.orchestrator_thread = None
            self.stop_requested.clear()
            self.set_orchestrator_state(False)
            return

        self.log(
            "자동 생산 시작 - amr에 RESET_SEQUENCE + START, 3abb·5abb에 Start를 보냅니다. "
            "출고 컨베이어는 AMR의 CONVEYOR_START(FWD) 로그를 확인한 뒤에만 돕니다 "
            "(백그라운드 _run_pickup_matcher가 처리, 자동 생산 루프는 관여하지 않음).",
            "orch",
        )
        self.done_events["3abb"].clear()
        self.done_events["5abb"].clear()
        for station in PICKUP_STATIONS:
            # 이전 실행에서 남았을 수 있는 신호를 비우고 새로 시작한다.
            for pending_queue in (self.ready_queues[station], self.amr_arrived_queues[station]):
                while not pending_queue.empty():
                    try:
                        pending_queue.get_nowait()
                    except queue.Empty:
                        break
            self.convey_done_events[station].clear()

        self.send("amr", AMR_RESET_COMMAND)
        self.send("amr", AMR_START_COMMAND)
        self.send("3abb", "Start")
        self.send("5abb", "Start")

        if not self.stop_requested.is_set():
            self.done_events["3abb"].wait()
            self.log("3abb 전체 작업 완료 확인 (Done)", "orch")

        if not self.stop_requested.is_set():
            self.done_events["5abb"].wait()
            self.log("5abb 전체 작업 완료 확인 (Done)", "orch")
            self.log("자동 생산 완료! (AMR의 물리적 왕복은 별도로 계속 진행 중일 수 있습니다)", "done")

        self.orchestrator_thread = None
        self.stop_requested.clear()
        self.set_orchestrator_state(False)

    def stop(self) -> None:
        self.running.clear()
        self.stop_requested.set()
        if self.server_socket is not None:
            try:
                self.server_socket.close()
            except OSError:
                pass
        if self.udp_socket is not None:
            try:
                self.udp_socket.close()
            except OSError:
                pass
        with self.relays_lock:
            relays = list(self.relays.values())
            self.relays.clear()
        for relay in relays:
            try:
                relay.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                relay.sock.close()
            except OSError:
                pass


# ----- Flask (웹 HMI) -----
app = Flask(__name__)
broadcaster = Broadcaster()
server = AdminServer(broadcaster)


INDEX_HTML = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AMR 통합 관리자 - 웹 HMI</title>
<style>
  :root {
    --bg: #0b1220; --panel: #111a2c; --panel-border: #1f2c47;
    --text: #d7e1f0; --muted: #7d8aa3; --accent: #22d3ee;
    --ok: #2ecc71; --err: #e74c3c; --warn: #f1c40f;
    --send: #a78bfa; --orch: #60a5fa; --idle: #3a4863;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--bg); color: var(--text);
    font-family: "Segoe UI", "Malgun Gothic", sans-serif;
  }
  header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 20px; background: linear-gradient(180deg, #101a30, #0b1220);
    border-bottom: 1px solid var(--panel-border);
  }
  header h1 { font-size: 18px; margin: 0; letter-spacing: 0.5px; }
  header h1 span { color: var(--accent); }
  #conn-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; background: var(--idle); }
  #conn-dot.live { background: var(--ok); box-shadow: 0 0 8px var(--ok); }
  #conn-dot.dead { background: var(--err); box-shadow: 0 0 8px var(--err); }
  main { padding: 16px 20px; display: grid; gap: 16px; max-width: 1200px; margin: 0 auto; }
  .panel {
    background: var(--panel); border: 1px solid var(--panel-border);
    border-radius: 10px; padding: 14px 16px;
  }
  .panel h2 {
    font-size: 12px; text-transform: uppercase; letter-spacing: 1px;
    color: var(--muted); margin: 0 0 12px 0;
  }
  #lamps { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; }
  .lamp-card {
    background: #0c1526; border: 1px solid var(--panel-border); border-radius: 8px;
    padding: 12px; display: flex; align-items: center; gap: 10px;
  }
  .lamp {
    width: 18px; height: 18px; border-radius: 50%; flex-shrink: 0;
    background: var(--idle); box-shadow: inset 0 0 4px #000;
    transition: background 0.15s, box-shadow 0.15s;
  }
  .lamp.ok, .lamp.done { background: var(--ok); box-shadow: 0 0 10px var(--ok); }
  .lamp.err { background: var(--err); box-shadow: 0 0 10px var(--err); }
  .lamp.warn { background: var(--warn); box-shadow: 0 0 10px var(--warn); }
  .lamp.cyan { background: var(--accent); box-shadow: 0 0 10px var(--accent); }
  .lamp-info { min-width: 0; }
  .lamp-name { font-weight: 600; font-size: 14px; }
  .lamp-text { font-size: 12px; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .row { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
  input, select, button {
    background: #0c1526; border: 1px solid var(--panel-border); color: var(--text);
    border-radius: 6px; padding: 8px 10px; font-size: 13px;
  }
  input { min-width: 120px; }
  button {
    cursor: pointer; border-color: #2a3a5c; transition: background 0.1s, border-color 0.1s;
  }
  button:hover { background: #16223d; border-color: var(--accent); }
  button.primary { background: #123049; border-color: var(--accent); color: var(--accent); }
  button.stop { border-color: var(--err); color: var(--err); }
  .quick-buttons button { padding: 6px 10px; }
  #log {
    background: #060c18; border: 1px solid var(--panel-border); border-radius: 8px;
    height: 340px; overflow-y: auto; padding: 10px 12px;
    font-family: Consolas, "D2Coding", monospace; font-size: 12.5px; line-height: 1.55;
  }
  #log .line { white-space: pre-wrap; word-break: break-word; }
  .tag-info { color: var(--text); }
  .tag-ok { color: var(--ok); }
  .tag-err { color: var(--err); }
  .tag-warn { color: var(--warn); }
  .tag-send { color: var(--send); }
  .tag-cyan { color: var(--accent); }
  .tag-done { color: var(--ok); font-weight: 600; }
  .tag-orch { color: var(--orch); }
  .hint { color: var(--muted); font-size: 12px; }
  #orch-state { font-size: 13px; padding: 4px 10px; border-radius: 6px; background: #0c1526; }
  #orch-state.running { color: var(--orch); border: 1px solid var(--orch); }
</style>
</head>
<body>
<header>
  <h1>AMR 통합 관리자 <span>- 웹 HMI</span></h1>
  <div><span id="conn-dot"></span><span id="conn-text" class="hint">연결 중...</span></div>
</header>
<main>
  <section class="panel">
    <h2>접속 현황</h2>
    <div id="lamps"></div>
  </section>

  <section class="panel">
    <h2>개별 명령 (이름 + 명령)</h2>
    <div class="row">
      <select id="target"></select>
      <input id="command" value="Start" placeholder="명령 입력 (예: Start)">
      <button class="primary" onclick="sendManual()">전송</button>
      <div class="quick-buttons row" id="quick-buttons"></div>
    </div>
  </section>

  <section class="panel">
    <h2>자동 생산 (3&rarr;4&rarr;3&rarr;5&rarr;4&rarr;5, 상부 항상 먼저)</h2>
    <div class="row">
      <button class="primary" onclick="startProduction()">자동 생산 시작</button>
      <button class="stop" onclick="stopProduction()">정지 요청</button>
      <span id="orch-state">대기 중</span>
      <span class="hint">(몇 개를 만들지는 3abb/5abb 쪽 RAPID가 정합니다 - 여기서는 Start를 한 번씩만 보냅니다)</span>
    </div>
  </section>

  <section class="panel">
    <h2>서버 로그</h2>
    <div id="log"></div>
  </section>
</main>

<script>
const KNOWN = {{ known_relays_json|safe }};
const lampsEl = document.getElementById('lamps');
const targetEl = document.getElementById('target');
const quickEl = document.getElementById('quick-buttons');
const logEl = document.getElementById('log');
const connDot = document.getElementById('conn-dot');
const connText = document.getElementById('conn-text');
const orchStateEl = document.getElementById('orch-state');

function buildStaticUI() {
  for (const name of KNOWN) {
    const card = document.createElement('div');
    card.className = 'lamp-card';
    card.id = 'lamp-card-' + name;
    card.innerHTML = `<div class="lamp" id="lamp-${name}"></div>
      <div class="lamp-info"><div class="lamp-name">${name}</div>
      <div class="lamp-text" id="lamp-text-${name}">대기 중...</div></div>`;
    lampsEl.appendChild(card);

    const opt = document.createElement('option');
    opt.value = name; opt.textContent = name;
    targetEl.appendChild(opt);
  }
  const allOpt = document.createElement('option');
  allOpt.value = 'all'; allOpt.textContent = 'all (전체)';
  targetEl.appendChild(allOpt);

  for (const name of ['3abb', '5abb', '4abb']) {
    const btn = document.createElement('button');
    btn.textContent = name + ' Start';
    btn.onclick = () => quickSend(name, 'Start');
    quickEl.appendChild(btn);
  }
}

function appendLog(time, message, tag) {
  const div = document.createElement('div');
  div.className = 'line tag-' + tag;
  div.textContent = `${time}  ${message}`;
  logEl.appendChild(div);
  logEl.scrollTop = logEl.scrollHeight;
}

function setLamp(name, text, tag) {
  const lamp = document.getElementById('lamp-' + name);
  const textEl = document.getElementById('lamp-text-' + name);
  if (!lamp || !textEl) return;
  lamp.className = 'lamp ' + tag;
  textEl.textContent = text;
}

function setOrchState(running) {
  orchStateEl.textContent = running ? '자동 생산 진행 중...' : '대기 중';
  orchStateEl.className = running ? 'running' : '';
}

async function loadState() {
  const res = await fetch('/api/state');
  const state = await res.json();
  for (const entry of state.log_history) appendLog(entry.time, entry.message, entry.tag);
  for (const [name, info] of Object.entries(state.relay_status)) setLamp(name, info.text, info.tag);
  setOrchState(state.orchestrator_running);
}

function connectStream() {
  const es = new EventSource('/api/stream');
  es.onopen = () => { connDot.className = 'live'; connText.textContent = '실시간 연결됨'; };
  es.onerror = () => { connDot.className = 'dead'; connText.textContent = '연결 끊김 - 재연결 시도 중'; };
  es.onmessage = (e) => {
    const data = JSON.parse(e.data);
    if (data.kind === 'log') appendLog(data.time, data.message, data.tag);
    else if (data.kind === 'relay_status') setLamp(data.name, data.text, data.tag);
    else if (data.kind === 'orch_state') setOrchState(data.running);
  };
}

async function postJson(url, body) {
  const res = await fetch(url, {
    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body || {}),
  });
  return res.json();
}

async function sendManual() {
  const target = targetEl.value;
  const command = document.getElementById('command').value.trim();
  if (!command) return;
  const result = await postJson('/api/send', {target, command});
  if (!result.ok) alert(result.error);
}

async function quickSend(target, command) {
  const result = await postJson('/api/send', {target, command});
  if (!result.ok) alert(result.error);
}

async function startProduction() {
  const result = await postJson('/api/produce', {});
  if (!result.ok) alert(result.error);
}

async function stopProduction() {
  await postJson('/api/produce/stop', {});
}

buildStaticUI();
loadState();
connectStream();
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(INDEX_HTML, known_relays_json=json.dumps(KNOWN_RELAYS, ensure_ascii=False))


@app.route("/api/state")
def api_state():
    return jsonify(server.snapshot())


@app.route("/api/stream")
def api_stream():
    def generate():
        subscriber_queue = broadcaster.subscribe()
        # 헤더가 첫 청크와 함께 전송되므로, 한동안 이벤트가 없어도 브라우저가
        # 곧바로 "연결됨" 상태를 인식하도록 접속 직후 즉시 한 줄을 보낸다.
        yield ": connected\n\n"
        try:
            while True:
                try:
                    item = subscriber_queue.get(timeout=10)
                    yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"
                except queue.Empty:
                    yield ": keep-alive\n\n"
        finally:
            broadcaster.unsubscribe(subscriber_queue)

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/api/send", methods=["POST"])
def api_send():
    data = request.get_json(force=True, silent=True) or {}
    target = str(data.get("target", "")).strip()
    command = str(data.get("command", "")).strip()
    if not target or not command:
        return jsonify(ok=False, error="대상과 명령을 모두 입력하세요."), 400
    ok, error = server.send(target, command)
    return jsonify(ok=ok, error=error)


@app.route("/api/produce", methods=["POST"])
def api_produce():
    ok, error = server.start_production()
    return jsonify(ok=ok, error=error)


@app.route("/api/produce/stop", methods=["POST"])
def api_produce_stop():
    server.request_stop_production()
    return jsonify(ok=True, error="")


def main() -> None:
    server.start()
    print(f"웹 HMI: http://localhost:{WEB_PORT}  (로봇/AMR 접속용 TCP 포트: {PORT}, AMR 탐색 UDP 포트: {UDP_PORT})")
    try:
        app.run(host="0.0.0.0", port=WEB_PORT, threaded=True)
    finally:
        server.stop()


if __name__ == "__main__":
    main()
