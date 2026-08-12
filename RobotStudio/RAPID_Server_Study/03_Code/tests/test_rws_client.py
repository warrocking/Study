import httpx
import pytest

from abb_bridge.rws_client import RwsClient, RwsWriteDisabled


@pytest.mark.asyncio
async def test_rws_read_uses_version_two_accept_header() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Accept"] == "application/hal+json;v=2.0"
        assert request.url.path == "/rw/system"
        return httpx.Response(200, json={"_embedded": {"_state": [{"name": "VC"}]}})

    client = RwsClient(
        base_url="https://controller.test",
        username="user",
        password="pass",
        api_version=2,
        transport=httpx.MockTransport(handler),
    )
    try:
        data = await client.get_system()
    finally:
        await client.aclose()
    assert data["_embedded"]["_state"][0]["name"] == "VC"


@pytest.mark.asyncio
async def test_rws_write_is_disabled_by_default() -> None:
    client = RwsClient(
        base_url="https://controller.test",
        username="user",
        password="pass",
        transport=httpx.MockTransport(lambda _: httpx.Response(204)),
    )
    try:
        with pytest.raises(RwsWriteDisabled):
            await client.set_rapid_symbol("T_ROB1", "BridgeMailbox", "gCmdSeq", "1")
    finally:
        await client.aclose()

