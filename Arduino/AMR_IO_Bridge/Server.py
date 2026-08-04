#!/usr/bin/env python3
"""Temporary Admin server for AMR_Admin_Arduino_Bridge.ino.

Protocol:
  * TCP server listens on port 5000.
  * A client sends its device name as the first newline-terminated line.
  * Following lines are displayed as status messages.
  * Admin commands use: <device-name> <command>
    Example: amr cycle

Only the Python standard library is required.
"""

from __future__ import annotations

import queue
import socket
import threading
import tkinter as tk
from dataclasses import dataclass
from datetime import datetime
from tkinter import messagebox, scrolledtext, ttk


HOST = "0.0.0.0"
PORT = 5000
MAX_LINE_BYTES = 2048


@dataclass
class Device:
    name: str
    sock: socket.socket
    address: tuple[str, int]
    lock: threading.Lock


class AdminServer:
    def __init__(self, event_queue: queue.Queue):
        self.events = event_queue
        self.devices: dict[str, Device] = {}
        self.devices_lock = threading.Lock()
        self.server_socket: socket.socket | None = None
        self.running = threading.Event()

    def log(self, message: str) -> None:
        self.events.put(("log", message))

    def publish_devices(self) -> None:
        with self.devices_lock:
            names = sorted(self.devices)
        self.events.put(("devices", names))

    def start(self) -> None:
        if self.running.is_set():
            return
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
            self.log(f"Admin server started: {HOST}:{PORT}")

            while self.running.is_set():
                try:
                    client, address = server.accept()
                except socket.timeout:
                    continue
                except OSError:
                    break
                threading.Thread(
                    target=self._handle_client,
                    args=(client, address),
                    daemon=True,
                ).start()
        except OSError as exc:
            self.log(f"SERVER ERROR: {exc}")
            self.events.put(("server_error", str(exc)))
        finally:
            self.running.clear()

    def _handle_client(self, client: socket.socket, address: tuple[str, int]) -> None:
        client.settimeout(15.0)
        device_name = ""
        reader = client.makefile("r", encoding="utf-8", errors="replace", newline="\n")
        try:
            first_line = reader.readline(MAX_LINE_BYTES)
            if not first_line:
                return
            device_name = first_line.strip()
            if not device_name or " " in device_name or len(device_name) > 40:
                self.log(f"Rejected client {address}: invalid device name")
                return

            client.settimeout(None)
            new_device = Device(device_name, client, address, threading.Lock())
            with self.devices_lock:
                old_device = self.devices.get(device_name)
                self.devices[device_name] = new_device
            if old_device is not None:
                try:
                    old_device.sock.close()
                except OSError:
                    pass

            self.log(f"[{device_name}] connected from {address[0]}:{address[1]}")
            self.publish_devices()

            for line in reader:
                line = line.rstrip("\r\n")
                if line:
                    self.log(f"[{device_name}] {line}")
        except (OSError, UnicodeError) as exc:
            if self.running.is_set():
                self.log(f"[{device_name or address[0]}] connection error: {exc}")
        finally:
            try:
                reader.close()
            except OSError:
                pass
            try:
                client.close()
            except OSError:
                pass
            if device_name:
                with self.devices_lock:
                    current = self.devices.get(device_name)
                    if current is not None and current.sock is client:
                        del self.devices[device_name]
                        removed = True
                    else:
                        removed = False
                if removed:
                    self.log(f"[{device_name}] disconnected")
                    self.publish_devices()

    def send(self, device_name: str, command: str) -> tuple[bool, str]:
        command = command.strip()
        if not command:
            return False, "Command is empty"
        with self.devices_lock:
            device = self.devices.get(device_name)
        if device is None:
            return False, f"Device '{device_name}' is not connected"
        try:
            with device.lock:
                device.sock.sendall((command + "\n").encode("utf-8"))
            self.log(f"[ADMIN -> {device_name}] {command}")
            return True, ""
        except OSError as exc:
            return False, f"Send failed: {exc}"

    def stop(self) -> None:
        self.running.clear()
        if self.server_socket is not None:
            try:
                self.server_socket.close()
            except OSError:
                pass
        with self.devices_lock:
            devices = list(self.devices.values())
            self.devices.clear()
        for device in devices:
            try:
                device.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                device.sock.close()
            except OSError:
                pass


class AdminApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AMR Temporary Admin Server")
        self.root.geometry("920x650")
        self.root.minsize(780, 560)

        self.events: queue.Queue = queue.Queue()
        self.server = AdminServer(self.events)
        self.device_var = tk.StringVar(value="amr")
        self.command_var = tk.StringVar(value="amr prepare")
        self.status_var = tk.StringVar(value=f"Starting server on TCP port {PORT}...")

        self._build_ui()
        self.server.start()
        self.root.after(100, self._process_events)
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=12)
        outer.pack(fill="both", expand=True)

        header = ttk.Frame(outer)
        header.pack(fill="x")
        ttk.Label(header, text="AMR Admin Test Server", font=("Arial", 16, "bold")).pack(side="left")
        ttk.Label(header, text=f"TCP {PORT}").pack(side="right")

        status = ttk.LabelFrame(outer, text="Connection", padding=10)
        status.pack(fill="x", pady=(12, 8))
        ttk.Label(status, textvariable=self.status_var).pack(side="left", fill="x", expand=True)
        ttk.Label(status, text="Target:").pack(side="left", padx=(12, 4))
        self.device_box = ttk.Combobox(
            status, textvariable=self.device_var, values=("amr",), width=18, state="normal"
        )
        self.device_box.pack(side="left")

        controls = ttk.LabelFrame(outer, text="AMR controls", padding=10)
        controls.pack(fill="x", pady=8)

        buttons = [
            ("1. Prepare / Diagnose", "prepare"),
            ("2. ARM motors", "arm"),
            ("3. START route ST1", "start"),
            ("STOP", "stop"),
            ("Status", "status"),
            ("Macro ST1", "macro1"),
            ("Macro ST2", "macro2"),
            ("Macro ST3", "macro3"),
            ("Route ST2", "route2"),
            ("Route ST3", "route3"),
            ("Full cycle (after test)", "cycle"),
            ("Conveyor OFF", "conveyor_off"),
        ]
        for index, (label, command) in enumerate(buttons):
            button = ttk.Button(controls, text=label, command=lambda cmd=command: self._send(cmd))
            button.grid(row=index // 4, column=index % 4, padx=5, pady=5, sticky="ew")
        for column in range(4):
            controls.columnconfigure(column, weight=1)

        command_frame = ttk.LabelFrame(outer, text="Command (example: amr cycle)", padding=10)
        command_frame.pack(fill="x", pady=8)
        entry = ttk.Entry(command_frame, textvariable=self.command_var)
        entry.pack(side="left", fill="x", expand=True)
        entry.bind("<Return>", lambda _event: self._send_entry())
        ttk.Button(command_frame, text="Send", command=self._send_entry).pack(side="left", padx=(8, 0))

        log_frame = ttk.LabelFrame(outer, text="Server / AMR log", padding=8)
        log_frame.pack(fill="both", expand=True, pady=(8, 0))
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap="word", state="disabled", font=("Consolas", 10))
        self.log_text.pack(fill="both", expand=True)

    def _append_log(self, message: str) -> None:
        stamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{stamp}  {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _send(self, command: str, device_name: str | None = None) -> None:
        target = (device_name or self.device_var.get()).strip()
        ok, error = self.server.send(target, command)
        if not ok:
            self._append_log(f"SEND ERROR: {error}")
            messagebox.showwarning("Cannot send command", error)

    def _send_entry(self) -> None:
        text = self.command_var.get().strip()
        if not text:
            return
        parts = text.split(maxsplit=1)
        if len(parts) == 2:
            target, command = parts
        else:
            target, command = self.device_var.get().strip(), parts[0]
        self._send(command, target)

    def _process_events(self) -> None:
        while True:
            try:
                event, payload = self.events.get_nowait()
            except queue.Empty:
                break
            if event == "log":
                self._append_log(payload)
                if payload.startswith("Admin server started"):
                    self.status_var.set(f"Server running on port {PORT} - waiting for Arduino")
            elif event == "devices":
                values = payload or ["amr"]
                self.device_box.configure(values=values)
                if "amr" in payload:
                    self.device_var.set("amr")
                    self.status_var.set("Arduino/AMR connected")
                elif payload:
                    self.device_var.set(payload[0])
                    self.status_var.set(f"Connected devices: {', '.join(payload)}")
                else:
                    self.status_var.set(f"Server running on port {PORT} - waiting for Arduino")
            elif event == "server_error":
                self.status_var.set(f"Server error: {payload}")
                messagebox.showerror("Server error", payload)
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
