#!/usr/bin/env python3
"""Server_admin_GUI.py (Server_admin_V3.py 기반)

관리자 서버를 터미널이 아니라 창(GUI)으로 띄운 버전. AMR 담당자가 보내주신
Server.py(Tkinter 기반 "AMR Temporary Admin Server")와 같은 방식 - 표준
라이브러리(tkinter, socket, threading, queue)만 사용해서 pip install 없이
파일 하나만 그대로 실행하면 됩니다.

FastAPI/Django 같은 웹 프레임워크는 안 썼습니다 - 그건 설치가 필요해서
"파일 하나만 받아서 그대로 실행" 원칙이 깨지고, 지금 이 정도 규모(로컬 GUI
하나)에는 굳이 웹 서버까지 띄울 이유가 없습니다.

Server_admin_V3.py와 기능은 동일합니다 (터미널 대신 창으로 보여줄 뿐):
  - 3abb/4abb/5abb/amr 접속 상태를 실시간으로 보여줌
  - "이름 명령" 수동 전송 (AMR 담당자 툴과 같은 입력 방식)
  - "produce <대수>" 자동 생산 - 3abb/5abb 동시 Start -> 완료된 쪽부터
    AMR이 3->4->3->5->4->5 순서로 이송(PPT 8번 슬라이드 기준, 상부가
    항상 먼저) -> 지정한 대수만큼 반복
  - AMR_COMMANDS / ARRIVED_KEYWORD는 아직 실제 값이 없어서 자리만 잡아둔
    자리표시자입니다 - V3와 동일하게 값만 나중에 채우면 됨.

네트워킹(AdminServer)과 화면(AdminApp)을 분리하고, 백그라운드 스레드는
Tkinter 위젯을 직접 건드리지 않고 queue.Queue로 이벤트만 넘긴 뒤 메인
스레드가 root.after()로 주기적으로 그 큐를 비우면서 화면을 갱신합니다 -
Tkinter는 스레드 세이프하지 않기 때문에 이 패턴이 필수입니다(AMR 담당자
툴도 정확히 같은 방식으로 만들어져 있었습니다).

실행:
    python Server_admin_GUI.py
"""

from __future__ import annotations

import queue
import socket
import threading
import tkinter as tk
from dataclasses import dataclass, field
from datetime import datetime
from tkinter import messagebox, scrolledtext, ttk


HOST = "0.0.0.0"
PORT = 5000
ENCODING = "utf-8"
BROADCAST_NAME = "all"
DONE_KEYWORD = "done"
# TODO: 실제 AMR 도착 신호 형식이 정해지면 바꿀 것 (Server_admin_V3.py와 동일한 자리표시자).
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


class AdminServer:
    """네트워킹 + 자동 생산 오케스트레이션. GUI는 전혀 모른다 - 전부
    event_queue로만 화면에 알린다."""

    def __init__(self, event_queue: "queue.Queue"):
        self.events = event_queue
        self.relays: dict[str, Relay] = {}
        self.relays_lock = threading.Lock()
        self.running = threading.Event()
        self.server_socket: socket.socket | None = None

        # 오케스트레이터가 기다리는 신호들 - Server_admin_V3.py와 동일한 이유로
        # 큐가 아니라 Event를 쓴다 (먼저 끝난 쪽 신호를 잃어버리지 않기 위함).
        self.done_events = {"3abb": threading.Event(), "5abb": threading.Event()}
        self.amr_arrived_event = threading.Event()
        self.orchestrator_thread: threading.Thread | None = None
        self.stop_requested = threading.Event()

    # ----- 화면에 보낼 이벤트 -----
    def log(self, message: str, tag: str = "info") -> None:
        self.events.put(("log", message, tag))

    def set_relay_status(self, name: str, text: str, tag: str) -> None:
        self.events.put(("relay_status", name, text, tag))

    def set_orchestrator_state(self, running: bool) -> None:
        self.events.put(("orch_state", running))

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
            # HEARTBEAT/STATUS는 로그에 안 남기고 상태판만 갱신 (터미널판과 동일한 이유)
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

    # ----- 자동 생산 오케스트레이터 (Server_admin_V3.py와 동일한 로직) -----
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


class AdminApp:
    LOG_TAG_COLORS = {
        "info": "black",
        "ok": "#0a7d2c",
        "err": "#c0392b",
        "warn": "#b8860b",
        "send": "#7d3c98",
        "cyan": "#0e7490",
        "done": "#0a7d2c",
        "orch": "#1d4ed8",
    }

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AMR 통합 관리자 서버")
        self.root.geometry("980x700")
        self.root.minsize(820, 600)

        self.events: "queue.Queue" = queue.Queue()
        self.server = AdminServer(self.events)

        self.relay_status_labels: dict[str, tk.Label] = {}
        self.target_var = tk.StringVar(value=KNOWN_RELAYS[0])
        self.command_var = tk.StringVar(value="Start")
        self.produce_count_var = tk.StringVar(value="2")
        self.status_var = tk.StringVar(value=f"서버 시작 중... (포트 {PORT})")

        self._build_ui()
        self.server.start()
        self.root.after(100, self._process_events)
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    # ----- UI 구성 -----
    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=12)
        outer.pack(fill="both", expand=True)

        header = ttk.Frame(outer)
        header.pack(fill="x")
        ttk.Label(header, text="AMR 통합 관리자 서버", font=("Arial", 16, "bold")).pack(side="left")
        ttk.Label(header, textvariable=self.status_var).pack(side="right")

        # ----- 접속 현황 -----
        status_frame = ttk.LabelFrame(outer, text="접속 현황", padding=10)
        status_frame.pack(fill="x", pady=(10, 8))
        for index, name in enumerate(KNOWN_RELAYS):
            cell = ttk.Frame(status_frame)
            cell.grid(row=0, column=index, padx=10, sticky="w")
            ttk.Label(cell, text=name, font=("Arial", 11, "bold")).pack(anchor="w")
            label = tk.Label(cell, text="대기 중...", fg="gray")
            label.pack(anchor="w")
            self.relay_status_labels[name] = label
        for index in range(len(KNOWN_RELAYS)):
            status_frame.columnconfigure(index, weight=1)

        # ----- 개별 명령 -----
        manual_frame = ttk.LabelFrame(outer, text="개별 명령 (이름 + 명령)", padding=10)
        manual_frame.pack(fill="x", pady=8)

        ttk.Label(manual_frame, text="대상:").pack(side="left")
        target_box = ttk.Combobox(
            manual_frame, textvariable=self.target_var,
            values=KNOWN_RELAYS + [BROADCAST_NAME], width=10, state="normal",
        )
        target_box.pack(side="left", padx=(4, 12))

        command_entry = ttk.Entry(manual_frame, textvariable=self.command_var)
        command_entry.pack(side="left", fill="x", expand=True)
        command_entry.bind("<Return>", lambda _event: self._send_manual())
        ttk.Button(manual_frame, text="전송", command=self._send_manual).pack(side="left", padx=(8, 0))

        quick_frame = ttk.Frame(manual_frame)
        quick_frame.pack(side="left", padx=(12, 0))
        for name in ("3abb", "5abb", "4abb"):
            ttk.Button(
                quick_frame, text=f"{name} Start",
                command=lambda n=name: self._quick_send(n, "Start"),
            ).pack(side="left", padx=2)

        # ----- 자동 생산 -----
        produce_frame = ttk.LabelFrame(outer, text="자동 생산 (3->4->3->5->4->5 반복, 상부 항상 먼저)", padding=10)
        produce_frame.pack(fill="x", pady=8)
        ttk.Label(produce_frame, text="목표 대수:").pack(side="left")
        ttk.Entry(produce_frame, textvariable=self.produce_count_var, width=6).pack(side="left", padx=(4, 12))
        ttk.Button(produce_frame, text="자동 생산 시작", command=self._start_production).pack(side="left")
        ttk.Button(produce_frame, text="정지 요청", command=self._stop_production).pack(side="left", padx=(8, 0))
        ttk.Label(
            produce_frame,
            text="(AMR 명령/도착 신호가 아직 자리표시자라 AMR 응답을 계속 기다리는 게 정상입니다)",
            foreground="gray",
        ).pack(side="left", padx=(12, 0))

        # ----- 로그 -----
        log_frame = ttk.LabelFrame(outer, text="서버 로그", padding=8)
        log_frame.pack(fill="both", expand=True, pady=(8, 0))
        self.log_text = scrolledtext.ScrolledText(
            log_frame, wrap="word", state="disabled", font=("Consolas", 10)
        )
        self.log_text.pack(fill="both", expand=True)
        for tag, color in self.LOG_TAG_COLORS.items():
            self.log_text.tag_configure(tag, foreground=color)

    # ----- 동작 -----
    def _send_manual(self) -> None:
        target = self.target_var.get().strip()
        command = self.command_var.get().strip()
        if not target or not command:
            return
        ok, error = self.server.send(target, command)
        if not ok:
            self._append_log(error, "err")
            messagebox.showwarning("전송 실패", error)

    def _quick_send(self, target: str, command: str) -> None:
        ok, error = self.server.send(target, command)
        if not ok:
            self._append_log(error, "err")
            messagebox.showwarning("전송 실패", error)

    def _start_production(self) -> None:
        try:
            car_count = int(self.produce_count_var.get().strip())
            if car_count <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("입력 오류", "목표 대수는 1 이상의 정수여야 합니다.")
            return
        ok, error = self.server.start_production(car_count)
        if not ok:
            self._append_log(error, "warn")
            messagebox.showinfo("자동 생산", error)

    def _stop_production(self) -> None:
        self.server.request_stop_production()

    # ----- 이벤트 큐 처리 (메인 스레드에서만 위젯을 건드림) -----
    def _append_log(self, message: str, tag: str) -> None:
        stamp = now()
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{stamp}  {message}\n", tag)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _process_events(self) -> None:
        while True:
            try:
                event = self.events.get_nowait()
            except queue.Empty:
                break

            kind = event[0]
            if kind == "log":
                _, message, tag = event
                self._append_log(message, tag)
                if "관리자 서버 시작됨" in message:
                    self.status_var.set(f"서버 실행 중 (포트 {PORT}) - 접속 대기 중")
            elif kind == "relay_status":
                _, name, text, tag = event
                label = self.relay_status_labels.get(name)
                if label is not None:
                    color = self.LOG_TAG_COLORS.get(tag, "black")
                    label.configure(text=text, fg=color)
            elif kind == "orch_state":
                _, running = event
                self.status_var.set("자동 생산 진행 중..." if running else f"서버 실행 중 (포트 {PORT})")

        self.root.after(100, self._process_events)

    def _close(self) -> None:
        self.server.stop()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    AdminApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
