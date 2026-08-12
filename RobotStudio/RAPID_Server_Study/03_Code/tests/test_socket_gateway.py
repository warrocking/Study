import asyncio

import pytest

from abb_bridge.service import BridgeService, MockController
from abb_bridge.socket_gateway import SocketGateway


@pytest.mark.asyncio
async def test_tcp_gateway_round_trip() -> None:
    gateway = SocketGateway(
        BridgeService(MockController()), host="127.0.0.1", port=0, command_timeout_seconds=1
    )
    await gateway.start()
    try:
        assert gateway.bound_port is not None
        reader, writer = await asyncio.open_connection("127.0.0.1", gateway.bound_port)
        writer.write(b"PING|rapid-e2e\r\n")
        await writer.drain()
        reply = await asyncio.wait_for(reader.readline(), timeout=1)
        writer.close()
        await writer.wait_closed()
    finally:
        await gateway.stop()

    assert reply.startswith(b"OK|rapid-e2e|completed|")
    assert reply.endswith(b"\r\n")
