# -*- coding: utf-8 -*-
"""
학습용 최소 프로토콜 모듈.

이 파일은 실제 서비스 코드가 아니라 "학습 자료"의 일부입니다.
0723_AMR_Project/Final_Ver07의 실제 프로토콜(ReadyForPickup / AmrArrived /
ConveyDone / EVENT PICKUP_ARRIVED 등)을 단순화한 버전으로,
- TCP 메시지 프레이밍(3부 3.4절)
- COMMAND / EVENT / STATUS / ACK / ERROR 구분
- unit / cycle / station 필드 파싱
을 눈으로 보고 직접 실행해볼 수 있도록 만들었습니다.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

MAX_LINE_LENGTH = 4096  # 실무 커뮤니티 공통 권장: 메시지 최대 길이 상한을 반드시 둘 것


class LineFramer:
    """TCP는 바이트 스트림일 뿐 메시지 경계가 없다.

    이 클래스는 '\\n'을 메시지 구분자로 써서, recv()가
      - 메시지 하나를 여러 조각으로 쪼개서 주거나
      - 여러 메시지를 한 번에 붙여서 주더라도
    항상 완전한 한 줄 단위로만 메시지를 꺼낼 수 있게 해준다.
    """

    def __init__(self, max_length: int = MAX_LINE_LENGTH):
        self._buffer = b""
        self._max_length = max_length

    def feed(self, chunk: bytes) -> list[str]:
        """recv()로 받은 원시 바이트 조각을 넣고, 완성된 줄들만 꺼낸다."""
        self._buffer += chunk
        if len(self._buffer) > self._max_length:
            # 실무에서 강조하는 안전장치: 개행이 계속 안 오는 잘못된 스트림이
            # 버퍼를 무한정 먹어치우는 것을 막는다.
            raise ValueError(
                f"버퍼가 최대 길이({self._max_length}바이트)를 넘었는데 "
                "완성된 줄이 없습니다 — 잘못된 스트림으로 판단하고 연결을 끊어야 합니다."
            )
        lines: list[str] = []
        while b"\n" in self._buffer:
            raw_line, self._buffer = self._buffer.split(b"\n", 1)
            text = raw_line.rstrip(b"\r").decode("utf-8", errors="replace")
            if text:  # 빈 줄은 무시
                lines.append(text)
        return lines


MESSAGE_TYPES = ("COMMAND", "EVENT", "STATUS", "ACK", "ERROR")

_FIELD_RE = re.compile(r"(\w+)=([^\s]+)")


@dataclass
class Message:
    """파싱된 한 줄짜리 프로토콜 메시지."""

    raw: str
    kind: str  # "command" | "event" | "status" | "ack" | "error" | "unknown"
    name: str  # 예: "ReadyForPickup", "PICKUP_ARRIVED", "Done"
    fields: dict = field(default_factory=dict)

    def get_int(self, key: str) -> Optional[int]:
        val = self.fields.get(key)
        if val is None:
            return None
        try:
            return int(val)
        except ValueError:
            return None


def parse_message(line: str) -> Message:
    """'EVENT PICKUP_ARRIVED station=3abb unit=2 cycle=2' 같은 한 줄을 구조화된 Message로 바꾼다.

    4부 프로토콜 설계 원칙(EVENT/COMMAND/STATUS를 명확히 구분)을 코드로 그대로 옮긴 것.
    """
    tokens = line.strip().split()
    if not tokens:
        return Message(raw=line, kind="unknown", name="")

    fields = dict(_FIELD_RE.findall(line))

    first = tokens[0].upper()
    if first in MESSAGE_TYPES:
        kind = first.lower()
        name = tokens[1] if len(tokens) > 1 else ""
    else:
        # Final_Ver07 실제 프로토콜처럼 타입 접두어 없이 이름만 오는 레거시 형태도 지원
        # (예: "ReadyForPickup unit=1", "Done")
        kind = "unknown"
        name = tokens[0]

    return Message(raw=line, kind=kind, name=name, fields=fields)


def format_event(name: str, **fields) -> str:
    """EVENT 메시지를 만들고 개행을 강제로 붙인다.

    1차 프로젝트 회고(3.2절: SocketSend는 줄바꿈을 자동으로 안 붙인다)의
    교훈을 코드로 강제한 것 — 개별적으로 매번 \\r\\n을 챙기지 않게 공용 함수 하나로 모음.
    """
    parts = [f"EVENT {name}"] + [f"{k}={v}" for k, v in fields.items()]
    return " ".join(parts) + "\n"
