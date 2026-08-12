from __future__ import annotations

import json
from dataclasses import dataclass

from pydantic import ValidationError

from .models import CommandRequest, CommandResponse, CommandType


class ProtocolError(ValueError):
    """Raised when an application frame cannot be decoded safely."""


@dataclass(frozen=True)
class DecodedFrame:
    command: CommandRequest
    wire_format: str


def _decode_pipe(text: str) -> CommandRequest:
    parts = text.split("|")
    verb = parts[0].upper()
    if verb == "PING" and len(parts) == 2:
        return CommandRequest(id=parts[1], type=CommandType.PING)
    if verb == "STATUS" and len(parts) == 2:
        return CommandRequest(id=parts[1], type=CommandType.GET_STATUS)
    if verb == "RESET" and len(parts) == 2:
        return CommandRequest(id=parts[1], type=CommandType.RESET_MOCK)
    if verb == "SET_DO" and len(parts) == 4 and parts[3] in {"0", "1"}:
        return CommandRequest(
            id=parts[1],
            type=CommandType.SET_DIGITAL_OUTPUT,
            payload={"signal": parts[2], "value": parts[3] == "1"},
        )
    raise ProtocolError("unsupported pipe frame")


def decode_frame(raw: bytes, *, max_bytes: int = 8192) -> DecodedFrame:
    """Decode one CRLF/LF-terminated application frame.

    TCP does not preserve application message boundaries. The caller must use
    StreamReader.readline/readuntil and impose a maximum length before calling.
    """
    if not raw or len(raw) > max_bytes:
        raise ProtocolError("frame is empty or exceeds the configured limit")
    try:
        text = raw.decode("utf-8").strip("\r\n")
    except UnicodeDecodeError as exc:
        raise ProtocolError("frame must be valid UTF-8") from exc
    if not text:
        raise ProtocolError("frame is empty")
    try:
        if text.startswith("{"):
            return DecodedFrame(CommandRequest.model_validate_json(text), "json")
        return DecodedFrame(_decode_pipe(text), "pipe")
    except (ValidationError, json.JSONDecodeError) as exc:
        raise ProtocolError("invalid command frame") from exc


def encode_response(response: CommandResponse, wire_format: str) -> bytes:
    if wire_format == "json":
        return response.model_dump_json(exclude_none=True).encode("utf-8") + b"\n"
    if wire_format == "pipe":
        state = "OK" if response.ok else "ERR"
        detail = json.dumps(
            response.payload if response.ok else {"error": response.error},
            ensure_ascii=True,
            separators=(",", ":"),
        )
        return f"{state}|{response.id}|{response.status}|{detail}\r\n".encode("ascii")
    raise ProtocolError(f"unknown wire format: {wire_format}")

