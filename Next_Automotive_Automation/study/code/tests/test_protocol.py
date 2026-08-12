# -*- coding: utf-8 -*-
"""
3부 3.4절 "TCP 메시지 프레이밍"에서 설명한 문제들을 실제 테스트 코드로 재현합니다.
회귀 테스트 목록(학습 자료용 SYSTEM_REQUIREMENTS 초안, 12~13번 항목)에 대응.
"""
import pytest

from mock_abb_controller.protocol import LineFramer, parse_message, format_event, MAX_LINE_LENGTH


def test_single_message_single_chunk():
    framer = LineFramer()
    lines = framer.feed(b"ReadyForPickup unit=1\n")
    assert lines == ["ReadyForPickup unit=1"]


def test_message_split_across_multiple_recv_calls():
    """회귀 테스트 13번: 한 메시지가 여러 TCP 패킷으로 나뉘는 경우."""
    framer = LineFramer()
    assert framer.feed(b"ReadyForPi") == []
    assert framer.feed(b"ckup unit=") == []
    assert framer.feed(b"1\n") == ["ReadyForPickup unit=1"]


def test_multiple_messages_in_single_recv_call():
    """회귀 테스트 12번: 여러 TCP 메시지가 붙어서 들어오는 경우 (Done + ReadyForPickup)."""
    framer = LineFramer()
    lines = framer.feed(b"Done\nReadyForPickup unit=2\n")
    assert lines == ["Done", "ReadyForPickup unit=2"]


def test_crlf_line_endings_are_stripped():
    framer = LineFramer()
    lines = framer.feed(b"ConveyDone unit=1\r\n")
    assert lines == ["ConveyDone unit=1"]


def test_oversized_stream_without_newline_raises():
    """실무 커뮤니티 공통 경고: 최대 길이 상한이 없으면 잘못된 스트림이 버퍼를 무한정 먹는다."""
    framer = LineFramer(max_length=16)
    with pytest.raises(ValueError):
        framer.feed(b"a" * (16 + 1))


def test_parse_event_with_fields():
    msg = parse_message("EVENT PICKUP_ARRIVED station=3abb unit=2 cycle=2 run=RUN-1")
    assert msg.kind == "event"
    assert msg.name == "PICKUP_ARRIVED"
    assert msg.get_int("unit") == 2
    assert msg.fields["station"] == "3abb"
    assert msg.fields["run"] == "RUN-1"


def test_parse_legacy_style_without_type_prefix():
    """Final_Ver07 실제 프로토콜처럼 타입 접두어 없이 오는 메시지도 파싱 가능해야 함."""
    msg = parse_message("ReadyForPickup unit=1")
    assert msg.name == "ReadyForPickup"
    assert msg.get_int("unit") == 1


def test_format_event_always_appends_newline():
    """1차 프로젝트 3.2절 교훈: SocketSend류 함수는 항상 개행을 강제로 붙여야 한다."""
    line = format_event("PICKUP_ARRIVED", station="3abb", unit=1)
    assert line.endswith("\n")
    assert "EVENT PICKUP_ARRIVED" in line
