# tcp_connection.py
#
# Generic TCP connection lifecycle: ask -> connect -> send/receive -> result -> close.
# Protocol-agnostic on purpose: no PLC/ABB naming here. Whatever the bytes mean
# is decided entirely by data_format.py. This class only knows how to open a
# TCP socket, push bytes out, and pull bytes back in - reusable for any TCP
# endpoint, not just this project's PLC or ABB robot.

import socket


class TcpConnection:
    def __init__(self, label):
        self.label = label
        self.ip = None
        self.port = None
        self.sock = None
        self.last_sent = None
        self.last_received = None
        self.error = None

    # ---- pre-connect ----
    def ask(self):
        self.ip = input(f"[{self.label}] IP address: ").strip()
        self.port = int(input(f"[{self.label}] Port: ").strip())

    # ---- connecting / session ----
    def connect(self, timeout=5.0):
        try:
            self.sock = socket.create_connection((self.ip, self.port), timeout=timeout)
            self.error = None
            return True
        except OSError as e:
            self.error = str(e)
            self.sock = None
            return False

    def send_bytes(self, data: bytes):
        if not self.sock:
            raise RuntimeError(f"[{self.label}] not connected")
        self.sock.sendall(data)
        self.last_sent = data

    def receive_bytes(self, size=1024, timeout=5.0) -> bytes:
        if not self.sock:
            raise RuntimeError(f"[{self.label}] not connected")
        self.sock.settimeout(timeout)
        data = self.sock.recv(size)
        self.last_received = data
        return data

    # ---- teardown ----
    def result(self):
        print(f"\n--- [{self.label}] result ---")
        print(f"  target    : {self.ip}:{self.port}")
        print(f"  connected : {self.sock is not None}")
        if self.error:
            print(f"  error     : {self.error}")
        if self.last_sent is not None:
            print(f"  last sent    : {self.last_sent!r}")
        if self.last_received is not None:
            print(f"  last received: {self.last_received!r}")

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None
