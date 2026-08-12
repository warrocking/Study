import pytest

from abb_bridge.models import CommandRequest, CommandType
from abb_bridge.service import BridgeService, MockController


@pytest.mark.asyncio
async def test_idempotent_command_id_returns_cached_response() -> None:
    service = BridgeService(MockController())
    command = CommandRequest(id="same-id", type=CommandType.PING)
    first = await service.handle(command)
    second = await service.handle(command)
    assert first == second
    assert first.ok is True


@pytest.mark.asyncio
async def test_set_digital_output_updates_mock_status() -> None:
    controller = MockController()
    service = BridgeService(controller)
    response = await service.handle(
        CommandRequest(
            id="do-1",
            type=CommandType.SET_DIGITAL_OUTPUT,
            payload={"signal": "doGrip", "value": True},
        )
    )
    status = await controller.get_status()
    assert response.ok is True
    assert status.digital_outputs["doGrip"] is True


@pytest.mark.asyncio
async def test_invalid_signal_is_rejected() -> None:
    service = BridgeService(MockController())
    response = await service.handle(
        CommandRequest(
            id="bad-do",
            type=CommandType.SET_DIGITAL_OUTPUT,
            payload={"signal": "not allowed!", "value": True},
        )
    )
    assert response.ok is False
    assert response.status == "rejected"

