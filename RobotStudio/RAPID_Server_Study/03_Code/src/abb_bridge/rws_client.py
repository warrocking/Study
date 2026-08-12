from __future__ import annotations

from typing import Any

import httpx


class RwsWriteDisabled(RuntimeError):
    pass


class RwsClient:
    """Small, version-aware RWS client for supervised data access.

    It intentionally does not expose motor, program-start, or motion commands.
    Controller permissions, mastership and safety configuration remain ABB-side
    responsibilities. Write access is disabled unless explicitly enabled.
    """

    def __init__(
        self,
        *,
        base_url: str,
        username: str,
        password: str,
        api_version: int = 2,
        verify_tls: bool = True,
        allow_writes: bool = False,
        timeout: float = 5.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.api_version = api_version
        self.allow_writes = allow_writes
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            auth=httpx.DigestAuth(username, password),
            verify=verify_tls,
            timeout=timeout,
            follow_redirects=True,
            transport=transport,
            headers=self._headers(),
        )

    def _headers(self) -> dict[str, str]:
        if self.api_version == 2:
            return {"Accept": "application/hal+json;v=2.0"}
        return {"Accept": "application/json"}

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _get_json(self, path: str, **params: str) -> dict[str, Any]:
        if self.api_version == 1:
            params.setdefault("json", "1")
        response = await self._client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    async def get_system(self) -> dict[str, Any]:
        return await self._get_json("/rw/system")

    async def get_rapid_symbol(self, task: str, module: str, symbol: str) -> dict[str, Any]:
        path = f"/rw/rapid/symbol/data/RAPID/{task}/{module}/{symbol}"
        return await self._get_json(path)

    async def set_rapid_symbol(
        self, task: str, module: str, symbol: str, rapid_literal: str
    ) -> None:
        if not self.allow_writes:
            raise RwsWriteDisabled("RWS writes are disabled; set RWS_ALLOW_WRITES only in a lab")
        path = f"/rw/rapid/symbol/data/RAPID/{task}/{module}/{symbol}"
        headers = (
            {"Content-Type": "application/x-www-form-urlencoded;v=2.0"}
            if self.api_version == 2
            else {"Content-Type": "application/x-www-form-urlencoded"}
        )
        response = await self._client.post(path, data={"value": rapid_literal}, headers=headers)
        response.raise_for_status()

