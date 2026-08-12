from __future__ import annotations

import asyncio
from collections import OrderedDict
from typing import Protocol

from .models import CommandRequest, CommandResponse, CommandType, ControllerStatus


class Controller(Protocol):
    async def execute(self, command: CommandRequest) -> dict: ...

    async def get_status(self) -> ControllerStatus: ...


class MockController:
    """Deterministic controller substitute for tests and first exercises."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._status = ControllerStatus()

    async def get_status(self) -> ControllerStatus:
        async with self._lock:
            return self._status.model_copy(deep=True)

    async def execute(self, command: CommandRequest) -> dict:
        async with self._lock:
            if command.type is CommandType.PING:
                result = {"message": "pong", "controller": self._status.controller}
            elif command.type is CommandType.GET_STATUS:
                result = self._status.model_dump(mode="json")
            elif command.type is CommandType.SET_DIGITAL_OUTPUT:
                signal = str(command.payload.get("signal", ""))
                value = command.payload.get("value")
                if not signal or not signal.replace("_", "").isalnum():
                    raise ValueError("payload.signal must be an alphanumeric RAPID I/O name")
                if not isinstance(value, bool):
                    raise ValueError("payload.value must be true or false")
                self._status.digital_outputs[signal] = value
                result = {"signal": signal, "value": value}
            elif command.type is CommandType.RESET_MOCK:
                self._status = ControllerStatus()
                result = {"reset": True}
            else:  # pragma: no cover - exhaustive guard
                raise ValueError(f"unsupported command type: {command.type}")
            self._status.last_command_id = command.id
            return result


class BridgeService:
    """Shared command layer used by both the HTTP API and TCP gateway."""

    def __init__(self, controller: Controller, *, history_size: int = 256) -> None:
        self.controller = controller
        self._history_size = history_size
        self._history: OrderedDict[str, CommandResponse] = OrderedDict()
        self._history_lock = asyncio.Lock()

    async def handle(self, command: CommandRequest) -> CommandResponse:
        async with self._history_lock:
            cached = self._history.get(command.id)
            if cached is not None:
                return cached.model_copy(deep=True)

        try:
            payload = await self.controller.execute(command)
            response = CommandResponse(
                id=command.id, ok=True, status="completed", payload=payload
            )
        except ValueError as exc:
            response = CommandResponse(
                id=command.id, ok=False, status="rejected", error=str(exc)
            )

        async with self._history_lock:
            self._history[command.id] = response
            self._history.move_to_end(command.id)
            while len(self._history) > self._history_size:
                self._history.popitem(last=False)
        return response.model_copy(deep=True)

