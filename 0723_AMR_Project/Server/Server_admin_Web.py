#!/usr/bin/env python3
"""Server_admin_Web.py (Server_admin_GUI.py 기반)

관리자 서버를 Tkinter 창이 아니라 웹 브라우저로 띄운 버전 - PLC의 HMI 화면처럼
브라우저에서 접속 상태(램프)와 로그를 실시간으로 보고 명령을 내릴 수 있습니다.
Flask가 필요합니다 (pip install flask, 이미 이 환경에 설치함).

Server_admin_GUI.py와 네트워킹/오케스트레이션 로직(AdminServer)은 완전히 동일합니다.
GUI 대신 Flask + Server-Sent Events(SSE)로 브라우저에 실시간으로 이벤트를
밀어 넣는다는 점만 다릅니다 - 여러 사람이 각자 브라우저로 같은 화면을 동시에
볼 수 있다는 게 Tkinter 버전 대비 이 버전의 장점입니다 (같은 네트워크 안에서
http://<이 PC의 IP>:{WEB_PORT}로 접속하면 됨).

  - 로봇/AMR 중계기들은 지금까지와 동일하게 TCP 포트 {PORT}로 접속합니다.
  - 사람은 웹 포트 {WEB_PORT}로 브라우저에서 접속합니다.
  - AMR_COMMANDS / ARRIVED_KEYWORD는 아직 자리표시자입니다 (V3/GUI와 동일).

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
# TODO: 실제 AMR 도착 신호 형식이 정해지면 바꿀 것 (V3/GUI와 동일한 자리표시자).
ARRIVED_KEYWORD = "arrived"

KNOWN_RELAYS = ["3abb", "4abb", "5abb", "amr"]

# TODO: 실제 AMR 매크로/루트 명령 이름이 정해지면 오른쪽 문자열만 교체할 것.
AMR_COMMANDS = {
    "goto_3_pickup": "GotoUpperPickup",
    "goto_4_drop_upper": "GotoDropoffUpper",
    "goto_3_return": "GotoUpperReturn",
    "goto_5_pickup": "GotoLowerPickup",
    "goto_4_drop_lower": "GotoDropoffLower",
    "goto_5_return": "GotoLowerReturn",
}


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
    """네트워킹 + 자동 생산 오케스트레이션. 화면(Flask/브라우저)은 전혀 모른다 -
    전부 event_queue(Broadcaster)로만 알린다. Server_admin_GUI.py의 AdminServer와
    로직은 동일하고, 새로고침/새 탭 대응을 위한 상태 스냅샷만 추가되었다."""

    def __init__(self, event_queue: "Broadcaster"):
        self.events = event_queue
        self.relays: dict[str, Relay] = {}
        self.relays_lock = threading.Lock()
        self.running = threading.Event()
        self.server_socket: socket.socket | None = None

        self.done_events = {"3abb": threading.Event(), "5abb": threading.Event()}
        self.amr_arrived_event = threading.Event()
        self.orchestrator_thread: threading.Thread | None = None
        self.stop_requested = threading.Event()

        # 브라우저가 새로고침하거나 새 탭을 열 때 SSE로 지나간 과거 이벤트를
        # 놓쳐도 바로 채워 넣을 수 있도록 최근 상태를 기억해 둔다.
        self.state_lock = threading.Lock()
        self.relay_status: dict[str, dict] = {}
        self.log_history: deque = deque(maxlen=300)
        self.orchestrator_running = False

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
            }

    # ----- 서버 -----
    def start(self) -> None:
        self.running.set()
        threading.Thread(target=self._serve, daemon=True).start()

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

        if DONE_KEYWORD in lowered and name in self.done_events:
            self.done_events[name].set()
            self.log(f"{name} 작업 완료! ({message})", "done")
            self.set_relay_status(name, f"{now()}  {message}", "done")
        elif name == "amr" and ARRIVED_KEYWORD in lowered:
            self.amr_arrived_event.set()
            self.log(f"amr 도착! ({message})", "done")
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

        return ok_all, ""

    # ----- 자동 생산 오케스트레이터 (Server_admin_V3.py / GUI와 동일한 로직) -----
    def start_production(self, car_count: int) -> tuple[bool, str]:
        if self.orchestrator_thread is not None:
            return False, "이미 자동 생산이 진행 중입니다."
        self.stop_requested.clear()
        self.orchestrator_thread = threading.Thread(
            target=self._run_production, args=(car_count,), daemon=True
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

    def _run_amr_leg(self, step_name: str, command_key: str) -> None:
        self.log(f"AMR -> {step_name}", "orch")
        self.amr_arrived_event.clear()
        self.send("amr", AMR_COMMANDS[command_key])
        self.amr_arrived_event.wait()   # AMR 도착 신호 형식이 정해지기 전까진 여기서 계속 대기(의도됨)
        self.log(f"AMR {step_name} 도착 확인", "orch")

    def _run_production(self, car_count: int) -> None:
        self.log(f"자동 생산 시작 - 목표 {car_count}대", "orch")

        for car_index in range(1, car_count + 1):
            if self.stop_requested.is_set():
                self.log("정지 요청으로 다음 차량 시작 전에 멈춥니다.", "warn")
                break

            self.log(f"{car_index}/{car_count}번째 차량 - 3abb·5abb 동시 시작", "orch")
            self.done_events["3abb"].clear()
            self.done_events["5abb"].clear()
            self.send("3abb", "Start")
            self.send("5abb", "Start")

            self.done_events["3abb"].wait()
            self.log("3abb 작업 완료 확인 - 상부 미션 시작", "orch")
            self._run_amr_leg("3abb 픽업", "goto_3_pickup")
            self._run_amr_leg("4abb 상부 하차", "goto_4_drop_upper")
            self._run_amr_leg("3abb 빈 파렛트 반납", "goto_3_return")

            if self.stop_requested.is_set():
                self.log("정지 요청으로 하부 이송 전에 멈춥니다.", "warn")
                break

            self.done_events["5abb"].wait()
            self.log("5abb 작업 완료 확인 - 하부 미션 시작", "orch")
            self._run_amr_leg("5abb 픽업", "goto_5_pickup")
            self._run_amr_leg("4abb 하부 하차", "goto_4_drop_lower")
            self._run_amr_leg("5abb 빈 파렛트 반납", "goto_5_return")

            self.log(f"{car_index}/{car_count}번째 차량 완료!", "done")

        self.log("자동 생산 종료", "orch")
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
    <h2>자동 생산 (3&rarr;4&rarr;3&rarr;5&rarr;4&rarr;5 반복, 상부 항상 먼저)</h2>
    <div class="row">
      <label class="hint">목표 대수</label>
      <input id="car-count" type="number" min="1" value="2" style="width:70px">
      <button class="primary" onclick="startProduction()">자동 생산 시작</button>
      <button class="stop" onclick="stopProduction()">정지 요청</button>
      <span id="orch-state">대기 중</span>
      <span class="hint">(AMR 명령/도착 신호가 아직 자리표시자라 AMR 응답을 계속 기다리는 게 정상입니다)</span>
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
  const count = parseInt(document.getElementById('car-count').value, 10);
  if (!count || count <= 0) { alert('목표 대수는 1 이상의 정수여야 합니다.'); return; }
  const result = await postJson('/api/produce', {count});
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
    data = request.get_json(force=True, silent=True) or {}
    try:
        count = int(data.get("count", 0))
        if count <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify(ok=False, error="목표 대수는 1 이상의 정수여야 합니다."), 400
    ok, error = server.start_production(count)
    return jsonify(ok=ok, error=error)


@app.route("/api/produce/stop", methods=["POST"])
def api_produce_stop():
    server.request_stop_production()
    return jsonify(ok=True, error="")


def main() -> None:
    server.start()
    print(f"웹 HMI: http://localhost:{WEB_PORT}  (로봇/AMR 접속용 TCP 포트: {PORT})")
    try:
        app.run(host="0.0.0.0", port=WEB_PORT, threaded=True)
    finally:
        server.stop()


if __name__ == "__main__":
    main()
