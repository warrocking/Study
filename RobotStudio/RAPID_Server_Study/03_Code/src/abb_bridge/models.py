from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CommandType(StrEnum):
    PING = "ping"
    GET_STATUS = "get_status"
    SET_DIGITAL_OUTPUT = "set_digital_output"
    RESET_MOCK = "reset_mock"


class CommandRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = Field(default=1, ge=1, le=1)
    id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_.:-]+$")
    type: CommandType
    payload: dict[str, Any] = Field(default_factory=dict)
    sent_at: datetime | None = None


class CommandResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = 1
    id: str
    ok: bool
    status: str
    payload: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ControllerStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    controller: str = "mock-controller"
    connected: bool = True
    operation_mode: str = "simulation"
    rapid_state: str = "stopped"
    motors_on: bool = False
    digital_outputs: dict[str, bool] = Field(default_factory=dict)
    last_command_id: str | None = None


class HealthResponse(BaseModel):
    status: str
    controller_mode: str
    tcp_gateway: str

