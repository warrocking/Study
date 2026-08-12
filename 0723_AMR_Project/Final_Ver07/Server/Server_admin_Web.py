#!/usr/bin/env python3
"""Server_admin_Web.py - Final_Ver07

Final_Ver07 안내:
  Final_Ver07은 Final_Ver05를 그대로 기반으로 합니다 - 서버/중계기/아두이노
  로직은 Final_Ver05와 완전히 동일하고, RAPID(3abb.mod/4abb.mod/5abb.mod)만
  사용자가 실제 로봇에서 직접 튜닝한 최신 속도/좌표 값을 그대로 반영했습니다
  (예: 도어 도킹 관련 MoveL을 v_slow에서 v_fast로 변경 등 - 실제 라이브
  파일에서 그대로 가져왔으며 임의로 되돌리지 않았습니다).

  Final_Ver06(다른 세션/codex가 만든 PICKUP_ARRIVED+ARRIVAL_ACK 핸드셰이크
  재설계)은 이 버전에 섞이지 않았습니다 - 사용자 요청에 따라 Final_Ver05를
  기반으로 새로 버전 관리를 시작한 것이 Final_Ver07이며, 앞으로의 버전 관리는
  이 폴더 계열(Final_Ver07 이상)에서만 이어집니다.


0723_AMR_Project/Final_Ver04/ 폴더는 Final_Ver03 대비 아두이노 펌웨어가
AMR_Server_Bridge_V25_FIXED_6S_RETURN_EXPLICIT_SIGNALS(Arduino/final_V03/
final_V03.ino, 이 폴더의 Arduino/AMR.ino에 사본 있음)로 교체되면서 서버의
AMR 이벤트 파싱 로직을 그에 맞게 다시 쓴 버전입니다. RAPID(3abb.mod/
4abb.mod/5abb.mod)와 3개 커넥터는 Final_Ver03과 동일 - ABB<->서버 프로토콜
(ReadyForPickup/AmrArrived/ConveyDone/Done)은 전혀 안 바뀌었고, 바뀐 건
서버가 amr 쪽 로그를 읽는 방식뿐입니다.

Final_Ver03(V16 펌웨어) 대비 이 버전에서 바뀐 것 - "태그 추측"에서 "명시적
station= 필드 직접 읽기"로:
  V16 펌웨어의 STATUS 로그에는 어느 스테이션 얘기인지 나와 있지 않아서,
  Final_Ver03의 서버는 "mode=UNTIL_D2가 붙어 있으면 3abb, step=4가 붙어
  있으면 5abb"라고 추측해야 했습니다. 이 V25 펌웨어는 관련된 모든 로그에
  station=3abb/station=4abb/station=5abb를 직접 박아서 보내므로, 서버는
  더 이상 추측할 필요가 없습니다.

  V25가 실제로 보내는, 이 서버가 쓰는 형식(모두 stationNameForStep()로 계산됨):
    - "STATUS CONVEYOR_START direction=FWD mode=... station=3abb ..." (ST1 적재)
    - "STATUS CONVEYOR_START direction=FWD mode=... station=5abb ..." (ST3 적재)
    - "STATUS CONVEYOR_START direction=FWD mode=ST2_RELOAD_UNTIL_D2 station=4abb ..."
      (ST2 재적재 - direction=FWD이지만 station이 4abb라서 대상 아님)
    - "STATUS CONVEYOR_START direction=REV ... station=..." (ST1/ST3 반납, ST2 하차 -
      direction이 REV라서 애초에 대상 아님)
  그래서 매칭 조건은 "direction=FWD 이면서 station=3abb 또는 station=5abb"
  하나로 단순해집니다 (아래 AMR_CONVEYOR_START_STATION_TO_PICKUP_STATION).

  V25는 또한 ARCL이 "Failed patrolling route ..., patrolling again"으로
  자체 재시도하는 상황을 더 이상 실패로 오인하지 않고 "EVENT ROUTE_RETRY"로만
  보고합니다(V24 FIXED-6S-RETURN 계열에 있던 버그 - 재시도 중인데 서버 쪽
  진행 상태를 통째로 리셋해버려서 AMR이 ST1 근처에서 계속 맴돌던 원인이었음).
  이 서버는 EVENT ROUTE_RETRY를 별도 처리 없이 일반 로그로만 보여줍니다 -
  게이팅 로직에는 영향 없음(정상적으로 계속 진행되는 신호이기 때문).

핵심 아이디어 - "AMR 펌웨어를 고치지 않고도, AMR이 이미 보내고 있는 STATUS
로그를 서버가 읽어서 출고 컨베이어를 AMR 도착 조건에 건다":
  이 펌웨어는 admin 소켓에 "START" 명령 1회를 받으면 ST1->ST2->ST1->ST3->
  ST2->ST3 6단계 왕복을 자동으로 "2 cycles" 실행합니다(=3abb/5abb가 Start
  1회에 만드는 차량 2대와 1:1 대응). "RUN ..." 개별 이동 명령은 명시적으로
  무시하며("STATUS RUN_IGNORED"), 진행 상황은 ARCL의 WaitState/Pausing
  감지에 맞춰 그때그때 STATUS/EVENT 로그로 그대로 보고합니다 - 서버는 이
  로그를 읽기만 하면 되고 펌웨어 코드는 전혀 바꾸지 않습니다.

  그래서 3abb/5abb의 컨베이어를 AMR 도착 확인 후로 게이팅합니다 (RAPID:
  3abb.mod/5abb.mod에 ReadyForPickup -> WaitForAmrArrived -> ConveyDone
  대기가 들어있음). 서버 쪽은 ABB의 "ReadyForPickup"과 AMR의 위 STATUS
  CONVEYOR_START 로그라는 서로 다른 두 이벤트 스트림을 스테이션별로
  매칭하는 백그라운드 스레드(_run_pickup_matcher)가 담당합니다 - 어느
  쪽이 먼저 도착하든 큐에 쌓아 두고 매칭되는 즉시 그 스테이션에
  "AmrArrived"를 보냅니다.

  AMR 펌웨어 코드 변경은 전혀 필요 없습니다 - 이미 나오고 있던 STATUS 로그를
  서버가 더 이상 무시하지 않는 것뿐입니다.

ver06 대비 이 버전(Server_admin_Web_ver07.py 동기화본)에서 추가된 것 -
8개 신호(3abb/5abb 각각 1번째 받기/반납/2번째 받기/반납) 전부 로그에서
구분하기:
  ver06까지는 "받기"(적재, direction=FWD) 4개만 unit=/cycle= 비교와 함께
  명시적으로 로그에 남았고, "반납"(direction=REV mode=RETURN_UNLOAD_6S) 4개는
  STATUS로 시작한다는 이유만으로 is_routine_status()에 흡수되어 상태판에만
  잠깐 찍히고 스크롤 로그에는 전혀 안 남았습니다. AMR_CONVEYOR_RETURN_KEYWORD
  + _handle_amr_conveyor_return_event()를 추가해서 이 4개도 "amr이 {station}
  {N}번째 반납(빈 팔레트/자재) 확인" 형태로 "orch" 태그를 달아 명확히
  구분되게 남깁니다. 다만 이 이벤트는 AmrArrived를 트리거하지 않습니다 -
  물리적 팔레트 반납은 di05_PLC_PlateReady/di09_Palette_Available를 PLC가
  직접 감지해서 처리하므로 서버가 개입할 필요가 없고, 이번 변경은 순수
  로깅/가시성 목적입니다(제어 흐름 변경 없음).

ver07 대비 이 버전(Final_Ver05, Server_admin_Web_ver08.py 동기화본)에서
바뀐 것 - 실제 운영 로그 재검증 중 발견한 두 가지 진짜 문제 수정:

  1) "번호 확인" 로그의 거짓 양성(false positive) 수정:
     ready_unit(ABB의 unit=)이나 arrived_cycle(amr의 cycle=) 중 하나라도
     None이면(=필드 자체가 없으면) 예전엔 그냥 else 분기로 빠져서
     "unit=None <-> amr cycle=1 일치"처럼 실제로는 비교를 안 했으면서
     "확인됨"이라고 거짓으로 로그를 남겼습니다. 실제 운영에서 로봇
     컨트롤러가 unit=을 전혀 안 보내는 상황(구버전 RAPID 프로그램이 남아
     있거나 재다운로드가 실제로 반영 안 된 경우 등)이 이 잘못된 "일치"
     로그에 가려져서 한참 늦게 발견됐습니다. 이제 필드가 하나라도 없으면
     "번호 확인 생략"이라고 "err" 태그로 눈에 띄게 남깁니다.

  2) amr "ERR ROUTE_FAILED" 발생 시 자동 생산이 무한 대기에 빠지는 문제
     수정: 펌웨어의 failActiveRoute()는 ARCL 경로가 진짜로 중단됐을 때
     (예: "Interrupted: Patrolling route ... once" - "patrolling again"
     자체 재시도와는 다름) 6단계 자동 시퀀스 전체를 리셋하고 스스로
     재시도하지 않습니다. 예전에는 이 상태에서 3abb/5abb가 이미 완성해
     놓은 몸체를 놓고 오지 않는 AMR을 기다리는 동안, _run_production()의
     done_events[station].wait()가 타임아웃 없이 영원히 블로킹해서 자동
     생산 스레드가 조용히 멈췄습니다(사용자 화면에는 스크롤되는 로그 한
     줄뿐이라 알아채기 어려움). 이제 amr_fault_event로 이 상태를 추적해서
     "[치명적]" 태그로 크게 알리고, 오케스트레이터는 1초마다 폴링하며 이
     상태를 감지하는 즉시 "자동 생산 중단"을 로그로 남기고 스스로
     빠져나옵니다. amr에 새 START/RESET_SEQUENCE를 보내면(수동이든 자동
     생산 재시작이든) 다음 시도로 간주해 상태를 지웁니다. 이 변경은 AMR이
     실제로 스스로 복구하도록 자동 재시도를 걸지는 않습니다 - 경로 중단은
     장애물/비상정지 등 실제 물리적 원인일 수 있어서, 사람이 원인을 확인한
     뒤 재개하는 쪽이 더 안전하다고 판단했습니다.

  RAPID(3abb.mod/4abb.mod/5abb.mod), 3개 중계기, 아두이노 펌웨어는 이번
  두 문제와 무관합니다(둘 다 순수 서버 로직 문제) - Final_Ver04와 완전히
  동일한 파일을 그대로 씁니다.

ver08 대비 이 버전(ver09)에서 바뀐 것 - 3개:

  3) 중계기(3abb_connector.py/5abb_connector.py)의 관리자->ABB 방향 버퍼
     드레인 버그 수정: ABB->관리자 방향은 진작 "한 번의 recv()에 여러 줄이
     섞여 들어올 수 있다"는 걸 감안한 드레인 루프가 있었는데, 반대 방향
     (관리자가 "Start"/"AmrArrived" 같은 명령을 ABB에 전달하는 쪽)엔 빠져
     있었다는 걸 재검증 중 발견했습니다. 관리자가 명령 두 개를 짧은 간격
     으로 보내 중계기 쪽 recv() 한 번에 같이 들어오면, 첫 줄만 ABB에
     전달되고 둘째 줄은 admin_buffer에 묻혀서 다음 관리자발 데이터가 올
     때까지(혹은 영원히) 로봇에 전달되지 않을 수 있었습니다. 재현 테스트로
     확인 후(고치기 전 코드로 돌리면 실패, 고친 후엔 통과) 두 중계기 모두
     같은 방식으로 드레인 루프를 추가했습니다. RAPID/서버/아두이노는 이
     변경과 무관합니다.

  4) _run_pickup_matcher()가 AmrArrived를 보낼 때, 그 판단의 근거가 된
     amr의 원본 메시지 전체를 같은 로그 줄에 그대로 남기도록 함 - "왜 지금
     출고했는지"를 나중에 로그만 보고도 원문으로 바로 확인할 수 있게 하기
     위한 순수 진단/가시성 목적 변경(제어 흐름 변경 없음).

  참고: "3abb가 첫 유닛 배송 후 AMR이 반납하러 돌아오기만 해도 2번째
  유닛을 출고해버린다"는 보고를 받고 FWD(픽업)/REV(반납) 구분 로직을
  재검증했지만(신규 fwd_rev_distinction_test.py 포함), 현재 서버/RAPID
  코드에서는 그 경로를 찾지 못했습니다. 과거 버전(Server_admin_Web_ver03.py
  이전)에는 "amr"발 메시지에 "arrived"라는 단어만 있으면(방향/스테이션
  구분 없이) 하나의 전역 이벤트를 세팅하는 구조가 실제로 있었던 걸 확인
  했지만, 그 버전은 ReadyForPickup/AmrArrived 프로토콜 자체가 없어서 지금
  RAPID와는 호환되지 않아 후보에서 제외했습니다. 실제 운영 중 재현되면
  "AmrArrived 전달, 출고 컨베이어 구동 대기 중 (근거 원본 메시지: ...)"
  로그 줄로 원인을 확정할 수 있습니다.

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
import re

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

# AMR(Arduino, AMR.ino V25)은 admin 소켓으로 "START" 명령 1회를 받으면
# ST1->ST2->ST1->ST3->ST2->ST3 6단계 왕복을 자동으로 2 cycle(=차량 2대분)
# 실행하는 자율 장비다. "RUN ..." 개별 이동 명령은 명시적으로 무시한다
# ("STATUS RUN_IGNORED"). 진행 상황은 STATUS/EVENT 로그로 실시간 보고되며,
# 이 서버는 그중 "STATUS CONVEYOR_START direction=FWD ... station=... ..."
# 로그만 골라 출고 컨베이어 게이팅에 쓴다 (아래 상수들 참고).
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
#   로그("STATUS CONVEYOR_START direction=FWD ... station=... ..."). direction=FWD만
#   "몸체를 실어 간다"는 뜻이고 direction=REV는 반납/하차 동작이라 AmrArrived
#   트리거 대상은 아니다(아래 AMR_CONVEYOR_RETURN_KEYWORD 참고 - 트리거는
#   안 하지만 로그로는 구분해서 보여준다).
AMR_CONVEYOR_START_KEYWORD = "conveyor_start direction=fwd"
# - amr -> 서버: AMR이 3abb/5abb에 빈 팔레트/자재를 반납하는 동작
#   ("STATUS CONVEYOR_START direction=REV mode=RETURN_UNLOAD_6S station=... ...").
#   물리적으로 팔레트가 돌아오면 di05_PLC_PlateReady/di09_Palette_Available를
#   PLC가 직접 감지해서 다음 유닛 조립이 진행되므로, 이 이벤트 자체는
#   AmrArrived처럼 서버가 ABB에 뭔가를 트리거해줄 필요가 없다 - 다만 "1번째
#   받기/반납, 2번째 받기/반납" 총 8개 신호를 전부 로그에서 구분해서 보고
#   싶다는 요청에 따라, 트리거 없이 로그만 남긴다. mode=ST2_UNLOAD_TIMER
#   (station=4abb, 픽업 스테이션 아님)는 이 키워드에 안 걸리므로 자연히
#   제외된다.
AMR_CONVEYOR_RETURN_KEYWORD = "conveyor_start direction=rev mode=return_unload_6s"

# 이 두 스테이션만 "픽업 대기 <-> AMR 도착 확인 -> 컨베이어 허가" 흐름을 탄다.
PICKUP_STATIONS = ("3abb", "5abb")

# V25 펌웨어는 관련 로그마다 station=3abb/station=4abb/station=5abb를 직접
# 박아서 보내므로(stationNameForStep() 참고), 더 이상 mode=/step= 태그로
# 추측할 필요가 없다. 적재(direction=FWD)와 반납(direction=REV) 로그 둘 다
# station=3abb 또는 station=5abb가 있는 경우에만 매칭한다 - station=4abb는
# 여기 없으므로 자연히 제외된다.
AMR_CONVEYOR_START_STATION_TO_PICKUP_STATION = (
    ("station=3abb", "3abb"),
    ("station=5abb", "5abb"),
)

# v08: amr -> 서버: "ERR ROUTE_FAILED route=... detail=..." - 펌웨어의
# failActiveRoute()가 호출됐다는 뜻으로, ARCL 경로가 진짜로 중단됐고(예:
# "Interrupted: Patrolling route ... once" - "Failed ..., patrolling again"
# 자체 재시도와는 다름) 6단계 자동 시퀀스 전체가 리셋되어 더 이상 스스로
# 진행하지 않는다(재시도 없음 - START/RESET_SEQUENCE를 다시 보내야 재개).
# 이걸 그냥 일반 "err" 태그 로그로만 흘려보내면, 3abb/5abb는 이미 완성해
# 놓은 몸체를 놓고 AMR을 하염없이 기다리는데(WaitForAmrArrived의 재시도
# 루프), 화면에는 그저 스크롤되는 로그 한 줄일 뿐이라 사람이 놓치기 쉽다.
# 그래서 별도 상태(amr_fault_event)로 추적해서 자동 생산 오케스트레이터가
# done_events를 무한정 기다리다 조용히 멈춰버리지 않고, 이 상태를 감지해서
# "라인이 멈췄다"고 즉시 알리고 스스로 빠져나오게 한다.
AMR_ROUTE_FAILED_KEYWORD = "err route_failed"

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


_NUMBER_FIELD_RE_CACHE: dict[str, "re.Pattern[str]"] = {}


def _extract_number_field(message: str | None, field_name: str) -> int | None:
    """"...unit=2..." 또는 "...cycle=1..." 같은 메시지에서 field_name= 뒤의
    정수를 뽑아낸다. 없거나 message가 None이면 None을 돌려준다 - 3abb/5abb의
    ReadyForPickup(unit=)과 amr의 STATUS(cycle=)를 서버가 직접 비교해서
    "몇 번째 유닛/사이클인지" 확인하는 데 쓴다."""
    if not message:
        return None
    pattern = _NUMBER_FIELD_RE_CACHE.get(field_name)
    if pattern is None:
        pattern = re.compile(rf"{re.escape(field_name)}=(\d+)", re.IGNORECASE)
        _NUMBER_FIELD_RE_CACHE[field_name] = pattern
    match = pattern.search(message)
    return int(match.group(1)) if match else None


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

        # v08: amr이 "ERR ROUTE_FAILED ..."를 보내면(진짜 경로 중단 - 자동
        # 재시도 없음) 켜진다. 자동 생산 오케스트레이터가 done_events를
        # 무한정 기다리다 멈추지 않고 이 상태를 보고 즉시 빠져나오는 데
        # 쓴다. amr에 새 START/RESET_SEQUENCE를 보내면(_clear_pickup_state
        # 참고) 새 시도로 간주하고 지운다.
        self.amr_fault_event = threading.Event()
        self.amr_fault_message: str | None = None

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
        """ready_queues[station](ABB의 ReadyForPickup unit=N)과
        amr_arrived_queues[station](AMR의 STATUS CONVEYOR_START ... cycle=N)를
        계속 지켜보다가 둘 다 준비되면 그 스테이션에 AmrArrived를 보내고
        ConveyDone까지 기다린다. 두 이벤트가 어느 순서로 오든(둘 다 큐라서
        먼저 온 쪽은 그냥 쌓여서 기다림) 상관없이 매칭한다. 생산 자동화
        여부와 무관하게 서버가 켜져 있는 동안 항상 돌아간다.

        v05: 짝을 맞출 때 큐 순서만 믿지 않고, ReadyForPickup의 unit=N과
        AMR STATUS의 cycle=N을 직접 파싱해서 같은 번호인지 확인하고 로그에
        남긴다 - "3abb 1번째 도착과 2번째 도착을 구분할 수 없냐"는 요청에
        따른 것. 순서 기반 매칭 자체는 이미 구조적으로 안전하지만(로봇은
        한 번에 한 유닛만 대기하고, Start마다 큐를 비움), 번호를 직접
        비교해서 로그에 남기면 혹시 모를 불일치를 바로 눈으로 확인할 수
        있다. 번호가 안 맞아도(원칙적으로 발생하면 안 됨) 생산 라인이
        멈추지 않도록 AmrArrived는 그대로 보내되, "err" 태그로 눈에 띄게
        경고한다."""
        while self.running.is_set():
            try:
                ready_message = self.ready_queues[station].get(timeout=1.0)
            except queue.Empty:
                continue

            ready_unit = _extract_number_field(ready_message, "unit")
            self.log(
                f"{station} 픽업 대기 중 (ReadyForPickup unit={ready_unit if ready_unit is not None else '?'}) "
                "- AMR 도착 확인 대기",
                "orch",
            )
            arrived_message = None
            while self.running.is_set():
                try:
                    arrived_message = self.amr_arrived_queues[station].get(timeout=1.0)
                    break
                except queue.Empty:
                    continue
            if not self.running.is_set():
                return

            arrived_cycle = _extract_number_field(arrived_message, "cycle")
            if ready_unit is None or arrived_cycle is None:
                # v08: 예전에는 이 경우도 그냥 else(=="일치") 분기로 빠져서
                # "unit=None <-> amr cycle=1 일치"처럼 실제로는 비교를 전혀
                # 안 했으면서 "확인됨"이라고 오해하게 로그가 남았다. 실제
                # 운영 로그에서 unit=이 아예 안 붙어 나오는 걸 이 잘못된
                # "일치" 로그가 가려서, 로봇 컨트롤러가 최신 RAPID 프로그램을
                # 안 쓰고 있다는 걸 한참 늦게 알아챈 사례가 있었다. 필드가
                # 하나라도 없으면 비교 자체를 생략했다는 걸 "err" 태그로
                # 눈에 띄게 알린다.
                self.log(
                    f"{station} 번호 확인 생략 (unit={ready_unit}, amr cycle={arrived_cycle} 중 "
                    "하나가 비어 있음 - RAPID 프로그램이 unit=번호를 보내는 최신 버전인지, "
                    "로봇 컨트롤러에 실제로 반영됐는지 확인 필요)",
                    "err",
                )
            elif ready_unit != arrived_cycle:
                self.log(
                    f"{station} 번호 불일치! ReadyForPickup unit={ready_unit} vs "
                    f"amr 도착 cycle={arrived_cycle} - 확인 필요 (그래도 AmrArrived는 전달함)",
                    "err",
                )
            else:
                self.log(
                    f"{station} 번호 확인됨: unit={ready_unit} <-> amr cycle={arrived_cycle} 일치",
                    "orch",
                )

            self.convey_done_events[station].clear()
            self.send(station, f"{AMR_ARRIVED_COMMAND} unit={ready_unit if ready_unit is not None else ''}".rstrip())
            # v08: 실제로 이 디스패치를 트리거한 원본 amr 메시지를 같은 줄에
            # 그대로 남긴다 - "3abb가 왜 지금 출고했지?"를 나중에 로그만
            # 보고도 100% 확정할 수 있게(FWD 픽업 도착이 맞는지, 혹시라도
            # 다른 무언가였는지 원본 텍스트로 바로 확인 가능).
            self.log(
                f"{station} -> AmrArrived 전달, 출고 컨베이어 구동 대기 중 "
                f"(근거 원본 메시지: {arrived_message})",
                "orch",
            )
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
        elif name == "amr" and AMR_CONVEYOR_RETURN_KEYWORD in lowered:
            self._handle_amr_conveyor_return_event(message, lowered)
        elif name == "amr" and AMR_ROUTE_FAILED_KEYWORD in lowered:
            self._handle_amr_route_failed_event(message)
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
        """amr이 "STATUS CONVEYOR_START direction=FWD ... station=... ..." 형태로
        보내는 로그를, 펌웨어가 직접 붙여 보내는 station= 필드로 해당 픽업
        스테이션의 amr_arrived_queues에 넣는다. direction=REV(반납/하차 동작)는
        애초에 이 핸들러까지 오지 않는다 - _handle_message에서
        AMR_CONVEYOR_START_KEYWORD("conveyor_start direction=fwd")로 이미
        걸러졌기 때문. station=4abb(ST2 재적재도 direction=FWD라서 여기까지는
        옴)는 이 핸드셰이크 대상이 아니므로 정상적으로, 자주 무시된다 -
        경고가 아니라 일반 로그로만 남긴다."""
        matched_station = None
        for tag, station in AMR_CONVEYOR_START_STATION_TO_PICKUP_STATION:
            if tag in lowered:
                matched_station = station
                break

        if matched_station is None:
            self.log(f"amr 컨베이어 구동 로그 (픽업 대상 스테이션 아님 - 무시): {message}", "cyan")
            self.set_relay_status("amr", f"{now()}  {message}", "cyan")
            return

        self.amr_arrived_queues[matched_station].put(message)
        self.log(f"amr이 {matched_station} 출고 컨베이어에 도착 확인: {message}", "done")
        self.set_relay_status("amr", f"{now()}  {message}", "done")

    def _handle_amr_conveyor_return_event(self, message: str, lowered: str) -> None:
        """amr이 "STATUS CONVEYOR_START direction=REV mode=RETURN_UNLOAD_6S
        station=... cycle=N ..." 형태로 보내는 반납(빈 팔레트/자재 반환) 로그를
        처리한다. 이 이벤트는 AmrArrived처럼 amr_arrived_queues에 넣지 않는다
        - 물리적으로 팔레트가 돌아오면 di05_PLC_PlateReady/di09_Palette_Available를
        PLC가 직접 감지해서 다음 유닛 조립을 이어가므로, 서버가 ABB에 별도로
        뭔가를 트리거해줄 필요가 없다. 다만 "1번째/2번째 받기·반납 총 8개
        신호를 전부 로그에서 구분해서 보고 싶다"는 요청에 따라, 트리거 없이
        로그만 명확히 구분해서 남긴다. station=4abb는 애초에
        AMR_CONVEYOR_RETURN_KEYWORD(mode=return_unload_6s)에 안 걸리므로(4abb는
        mode=ST2_UNLOAD_TIMER를 씀) 여기까지 오지 않는다."""
        matched_station = None
        for tag, station in AMR_CONVEYOR_START_STATION_TO_PICKUP_STATION:
            if tag in lowered:
                matched_station = station
                break

        cycle = _extract_number_field(message, "cycle")
        cycle_text = f"{cycle}번째" if cycle is not None else "?번째"

        if matched_station is None:
            self.log(f"amr 반납 컨베이어 구동 로그 (픽업 대상 스테이션 아님 - 무시): {message}", "cyan")
            self.set_relay_status("amr", f"{now()}  {message}", "cyan")
            return

        self.log(f"amr이 {matched_station} {cycle_text} 반납(빈 팔레트/자재) 확인: {message}", "orch")
        self.set_relay_status("amr", f"{now()}  {message}", "cyan")

    def _handle_amr_route_failed_event(self, message: str) -> None:
        """amr이 "ERR ROUTE_FAILED route=... detail=..."를 보내면 호출된다.
        펌웨어의 failActiveRoute()가 실행됐다는 뜻이고, 이건 6단계 자동
        시퀀스 전체를 리셋하며 스스로 재시도하지 않는다(예:
        "Interrupted: Patrolling route ROUTE_ST3 once" - "patrolling again"
        자체 재시도와 다르게 진짜 중단). 이후 3abb/5abb는 이미 완성해 놓은
        몸체를 놓고 오지 않는 AMR을 WaitForAmrArrived에서 계속 기다리게
        되므로, 이 상태를 amr_fault_event로 남겨서 자동 생산
        오케스트레이터(_run_production)가 done_events를 무한정 기다리다
        조용히 멈추지 않고 즉시 이 사실을 알리고 빠져나오게 한다."""
        self.amr_fault_message = message
        self.amr_fault_event.set()
        self.log(
            f"[치명적] amr 경로 실패로 자동 시퀀스가 중단되었습니다 (자동 재시도 없음): {message} "
            "- 원인(장애물/비상정지/네트워크 등)을 확인한 뒤 amr에 START 또는 RESET_SEQUENCE를 "
            "다시 보내야 재개됩니다.",
            "err",
        )
        self.set_relay_status("amr", f"{now()}  [치명적] {message}", "err")

    def _clear_pickup_state(self, station: str) -> None:
        """station의 ReadyForPickup/AMR 도착 큐와 ConveyDone 이벤트를 전부
        비운다.

        예전에는 이 정리가 _run_production() 안, "자동 생산 시작" 버튼을 눌렀을
        때만 실행됐다. 그런데 실제로는 그 버튼을 안 거치고 웹 화면의 "개별
        명령"이나 quick 버튼으로 3abb/5abb/amr에 수동으로 Start를 보내는
        경우가 많았는데, 그럴 땐 이전 실행(심지어 중간에 끊겼거나 수동으로
        재시도했던 테스트)에서 큐에 남아있던 신호가 전혀 안 지워진 채로
        남아있었다. 그 상태에서 다시 Start를 보내면, 이번 실행에서 AMR이
        실제로 아직 그 스테이션에 도착하지도 않았는데 예전에 남아있던
        "AMR 도착" 신호와 즉시 짝지어져서 컨베이어가 먼저 돌아버리는 문제가
        있었다("AMR이 5abb에 있는데 3abb가 출고했다" 증상의 원인으로 추정).
        이제 Start가 나가는 모든 경로(send()에서 공통 처리)에서 이 정리를
        거치게 해서, 수동으로 보내든 자동 생산으로 보내든 항상 깨끗한
        상태에서 시작한다."""
        for pending_queue in (self.ready_queues[station], self.amr_arrived_queues[station]):
            while not pending_queue.empty():
                try:
                    pending_queue.get_nowait()
                except queue.Empty:
                    break
        self.convey_done_events[station].clear()

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

        command_lower = command.lower()
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
            if relay.name == FOUR_ABB_NAME and command_lower == START_COMMAND.lower():
                self._mark_4abb_started()
                self.set_relay_status(
                    FOUR_ABB_NAME, f"{now()}  PLC 센서 감시·적재 대기 활성화", "ok"
                )

            # 3abb/5abb에 Start가 나가거나 amr에 START/RESET_SEQUENCE가 나가면,
            # 그 스테이션의 픽업 핸드셰이크 상태를 항상 깨끗하게 비운다 -
            # _clear_pickup_state() 위 설명 참고. 수동 전송이든 자동 생산
            # 오케스트레이터를 통한 전송이든 이 경로를 전부 거친다.
            if relay.name in PICKUP_STATIONS and command_lower == START_COMMAND.lower():
                self._clear_pickup_state(relay.name)
            if relay.name == "amr" and command.strip().upper() in (
                AMR_START_COMMAND.upper(), AMR_RESET_COMMAND.upper()
            ):
                for station in PICKUP_STATIONS:
                    self._clear_pickup_state(station)
                # v08: 새 START/RESET_SEQUENCE는 "이제부터 새 시도"라는
                # 뜻이므로, 이전에 남아있던 amr 경로 실패 상태도 같이
                # 지운다 - 안 지우면 다음 생산이 정상 진행돼도
                # amr_fault_event가 계속 켜진 채로 남아 있게 된다.
                self.amr_fault_event.clear()
                self.amr_fault_message = None

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
        # 픽업 상태 정리는 이제 send()가 Start/START/RESET_SEQUENCE 전송마다
        # 공통으로 처리한다(_clear_pickup_state() 참고) - 아래 send() 호출들이
        # 알아서 정리하므로 여기서 따로 반복할 필요가 없다.

        self.send("amr", AMR_RESET_COMMAND)
        self.send("amr", AMR_START_COMMAND)
        self.send("3abb", "Start")
        self.send("5abb", "Start")

        if not self.stop_requested.is_set():
            result = self._wait_for_station_done("3abb")
            if result == "fault":
                self._abort_production_on_fault("3abb")
                return
            if result == "done":
                self.log("3abb 전체 작업 완료 확인 (Done)", "orch")

        if not self.stop_requested.is_set():
            result = self._wait_for_station_done("5abb")
            if result == "fault":
                self._abort_production_on_fault("5abb")
                return
            if result == "done":
                self.log("5abb 전체 작업 완료 확인 (Done)", "orch")
                self.log("자동 생산 완료! (AMR의 물리적 왕복은 별도로 계속 진행 중일 수 있습니다)", "done")

        self.orchestrator_thread = None
        self.stop_requested.clear()
        self.set_orchestrator_state(False)

    def _wait_for_station_done(self, station: str) -> str:
        """station의 done_events를 기다리되, 예전처럼 타임아웃 없이 영원히
        블로킹하지 않는다. amr_fault_event가 켜지면(진짜 ARCL 경로 실패로
        6단계 자동 시퀀스가 스스로 리셋되어 다시는 돌아오지 않는 상황)
        "이 station의 Done을 기다리는 게 의미 없다"고 판단하고 즉시 빠져
        나온다 - 예전에는 이 상태에서 done_events.wait()가 done_events가
        영원히 안 켜지므로 자동 생산 스레드가 조용히 무한 대기에 빠졌었다.
        stop_requested(사용자의 "정지 요청")도 같은 이유로 폴링한다."""
        while True:
            if self.done_events[station].wait(timeout=1.0):
                return "done"
            if self.amr_fault_event.is_set():
                return "fault"
            if self.stop_requested.is_set():
                return "stopped"

    def _abort_production_on_fault(self, waiting_on_station: str) -> None:
        self.log(
            f"자동 생산 중단: amr 경로 실패로 {waiting_on_station}의 완료(Done)를 더 이상 "
            f"기다리지 않습니다 ({self.amr_fault_message or 'ERR ROUTE_FAILED'}). "
            "원인을 확인한 뒤 amr에 START/RESET_SEQUENCE를 다시 보내고 자동 생산을 재시작하세요.",
            "err",
        )
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
