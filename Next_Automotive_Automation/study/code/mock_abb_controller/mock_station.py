# -*- coding: utf-8 -*-
"""
Mock ABB Station — 실제 ABB 로봇 없이 3abb/5abb 스타일 핸드셰이크를 연습하기 위한
독립 실행형 TCP 서버.

마스터 프롬프트 7절이 요구한 "ABB가 없어도 Ready/Done 신호를 발생시킬 수 있는
가상 중계기"를 학습용으로 최소 구현한 것입니다.

실행법:
    python mock_station.py --station 3abb --port 6001 --units 2

동작:
    접속을 받으면 "Start"를 기다리다가, 받으면 unit 1..N에 대해
        ReadyForPickup unit=N
        (서버로부터 AmrArrived unit=N 을 받을 때까지 대기)
        ConveyDone unit=N
    을 순서대로 보내고, 마지막에 Done을 보냅니다.

    실제 Final_Ver07/Rapid/3abb.mod의 정상 순서(README.md 참고)를 그대로 흉내낸 것입니다.
"""
from __future__ import annotations

import argparse
import socket
import threading
import time

from protocol import LineFramer, parse_message


class MockStation:
    def __init__(self, station: str, port: int, units: int = 2, host: str = "0.0.0.0"):
        self.station = station
        self.port = port
        self.units = units
        self.host = host

    def serve_once(self) -> None:
        """접속 하나를 받아서 한 번의 생산 시퀀스를 실행하고 종료한다 (학습용 단순화)."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind((self.host, self.port))
            srv.listen(1)
            print(f"[{self.station}] 대기 중 (port={self.port}) — 서버 접속을 기다립니다.")
            conn, addr = srv.accept()
            print(f"[{self.station}] 연결됨: {addr}")
            with conn:
                self._run_sequence(conn)

    def _send(self, conn: socket.socket, line: str) -> None:
        # 1차 프로젝트 교훈: SocketSend는 개행을 자동으로 안 붙인다 — 항상 명시적으로 붙인다.
        payload = (line + "\n").encode("utf-8")
        conn.sendall(payload)
        print(f"[{self.station}] -> {line}")

    def _wait_for(self, conn: socket.socket, framer: LineFramer, expect_name: str, timeout: float = 30.0):
        conn.settimeout(timeout)
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                raise ConnectionError(f"[{self.station}] 연결이 끊겼습니다 ({expect_name} 대기 중)")
            for line in framer.feed(chunk):
                msg = parse_message(line)
                print(f"[{self.station}] <- {line}")
                if msg.name == expect_name or line.strip() == expect_name:
                    return msg

    def _run_sequence(self, conn: socket.socket) -> None:
        framer = LineFramer()
        self._wait_for(conn, framer, "Start")
        for unit in range(1, self.units + 1):
            time.sleep(0.3)  # 조립하는 척 흉내
            self._send(conn, f"ReadyForPickup unit={unit}")
            self._wait_for(conn, framer, f"AmrArrived unit={unit}")
            self._send(conn, f"ConveyDone unit={unit}")
        self._send(conn, "Done")
        print(f"[{self.station}] 시퀀스 완료")


def main() -> None:
    parser = argparse.ArgumentParser(description="Mock ABB Station 서버")
    parser.add_argument("--station", default="3abb")
    parser.add_argument("--port", type=int, default=6001)
    parser.add_argument("--units", type=int, default=2)
    args = parser.parse_args()
    MockStation(args.station, args.port, args.units).serve_once()


if __name__ == "__main__":
    main()
