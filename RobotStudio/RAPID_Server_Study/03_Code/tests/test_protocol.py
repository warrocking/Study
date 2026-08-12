import pytest

from abb_bridge.models import CommandResponse, CommandType
from abb_bridge.protocol import ProtocolError, decode_frame, encode_response


def test_decode_json_frame() -> None:
    decoded = decode_frame(b'{"version":1,"id":"cmd-1","type":"ping","payload":{}}\n')
    assert decoded.wire_format == "json"
    assert decoded.command.type is CommandType.PING


def test_decode_rapid_pipe_frame() -> None:
    decoded = decode_frame(b"SET_DO|rapid-2|doGrip|1\r\n")
    assert decoded.wire_format == "pipe"
    assert decoded.command.payload == {"signal": "doGrip", "value": True}


def test_rejects_bad_frame() -> None:
    with pytest.raises(ProtocolError):
        decode_frame(b"SET_DO|missing-fields\r\n")


def test_pipe_response_is_crlf_terminated() -> None:
    raw = encode_response(
        CommandResponse(id="cmd-1", ok=True, status="completed", payload={"message": "pong"}),
        "pipe",
    )
    assert raw.endswith(b"\r\n")
    assert raw.startswith(b"OK|cmd-1|completed|")

