from __future__ import annotations

import asyncio
import contextlib
import logging

from .protocol import ProtocolError, decode_frame, encode_response
from .service import BridgeService

LOGGER = logging.getLogger(__name__)


class SocketGateway:
    def __init__(
        self,
        service: BridgeService,
        *,
        host: str,
        port: int,
        max_frame_bytes: int = 8192,
        command_timeout_seconds: float = 3.0,
    ) -> None:
        self.service = service
        self.host = host
        self.port = port
        self.max_frame_bytes = max_frame_bytes
        self.command_timeout_seconds = command_timeout_seconds
        self._server: asyncio.Server | None = None

    @property
    def state(self) -> str:
        return "running" if self._server is not None else "stopped"

    @property
    def bound_port(self) -> int | None:
        if self._server is None or not self._server.sockets:
            return None
        return int(self._server.sockets[0].getsockname()[1])

    async def start(self) -> None:
        if self._server is None:
            self._server = await asyncio.start_server(self._handle_client, self.host, self.port)
            sockets = self._server.sockets or []
            LOGGER.info("TCP gateway listening on %s", [s.getsockname() for s in sockets])

    async def stop(self) -> None:
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None

    async def _handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        peer = writer.get_extra_info("peername")
        LOGGER.info("TCP client connected: %s", peer)
        try:
            while True:
                try:
                    raw = await reader.readuntil(b"\n")
                except asyncio.IncompleteReadError as exc:
                    if exc.partial:
                        LOGGER.warning("discarding unterminated frame from %s", peer)
                    break
                except asyncio.LimitOverrunError:
                    LOGGER.warning("oversized frame from %s", peer)
                    break

                try:
                    decoded = decode_frame(raw, max_bytes=self.max_frame_bytes)
                    response = await asyncio.wait_for(
                        self.service.handle(decoded.command),
                        timeout=self.command_timeout_seconds,
                    )
                    writer.write(encode_response(response, decoded.wire_format))
                    await writer.drain()
                except (ProtocolError, TimeoutError) as exc:
                    writer.write(f"ERR|unknown|rejected|{exc}\r\n".encode("ascii", "replace"))
                    await writer.drain()
        finally:
            writer.close()
            with contextlib.suppress(ConnectionError):
                await writer.wait_closed()
            LOGGER.info("TCP client disconnected: %s", peer)
