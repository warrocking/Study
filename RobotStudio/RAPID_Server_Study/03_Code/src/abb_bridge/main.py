from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status

from .config import BridgeSettings, get_settings
from .models import CommandRequest, CommandResponse, ControllerStatus, HealthResponse
from .service import BridgeService, MockController
from .socket_gateway import SocketGateway


def create_app(settings: BridgeSettings | None = None) -> FastAPI:
    cfg = settings or get_settings()
    controller = MockController()
    service = BridgeService(controller)
    gateway = SocketGateway(
        service,
        host=cfg.tcp_host,
        port=cfg.tcp_port,
        max_frame_bytes=cfg.max_frame_bytes,
        command_timeout_seconds=cfg.command_timeout_seconds,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.bridge_service = service
        app.state.socket_gateway = gateway
        if cfg.start_tcp_gateway:
            await gateway.start()
        try:
            yield
        finally:
            await gateway.stop()

    app = FastAPI(
        title="ABB RAPID Bridge Lab",
        version="0.1.0",
        description="Mock-first HTTP and TCP bridge for ABB RAPID communication study",
        lifespan=lifespan,
    )
    app.state.settings = cfg
    app.state.bridge_service = service
    app.state.socket_gateway = gateway

    async def require_api_key(
        x_bridge_key: str | None = Header(default=None),
    ) -> None:
        expected = cfg.api_key.get_secret_value()
        if not x_bridge_key or x_bridge_key != expected:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid API key")

    def get_service(request: Request) -> BridgeService:
        return request.app.state.bridge_service

    bridge_dependency = Depends(get_service)

    @app.get("/health", response_model=HealthResponse)
    async def health(request: Request) -> HealthResponse:
        return HealthResponse(
            status="ok",
            controller_mode=cfg.controller_mode,
            tcp_gateway=request.app.state.socket_gateway.state,
        )

    @app.get(
        "/v1/status",
        response_model=ControllerStatus,
        dependencies=[Depends(require_api_key)],
    )
    async def controller_status(
        bridge: BridgeService = bridge_dependency,
    ) -> ControllerStatus:
        return await bridge.controller.get_status()

    @app.post(
        "/v1/commands",
        response_model=CommandResponse,
        dependencies=[Depends(require_api_key)],
    )
    async def submit_command(
        command: CommandRequest,
        bridge: BridgeService = bridge_dependency,
    ) -> CommandResponse:
        return await bridge.handle(command)

    return app


app = create_app()
