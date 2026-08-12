from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class BridgeSettings(BaseSettings):
    """Runtime configuration loaded from ABB_BRIDGE_* environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="ABB_BRIDGE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_host: str = "127.0.0.1"
    api_port: int = Field(default=8000, ge=1, le=65535)
    api_key: SecretStr = SecretStr("lab-only-change-me")
    tcp_host: str = "127.0.0.1"
    tcp_port: int = Field(default=9100, ge=1, le=65535)
    start_tcp_gateway: bool = False
    controller_mode: Literal["mock", "rws"] = "mock"

    rws_base_url: str = "https://192.0.2.10"
    rws_username: str = "Default User"
    rws_password: SecretStr = SecretStr("robotics")
    rws_api_version: Literal[1, 2] = 2
    rws_verify_tls: bool = True
    rws_allow_writes: bool = False
    request_timeout_seconds: float = Field(default=5.0, gt=0, le=60)

    max_frame_bytes: int = Field(default=8192, ge=256, le=65536)
    command_timeout_seconds: float = Field(default=3.0, gt=0, le=30)


@lru_cache
def get_settings() -> BridgeSettings:
    return BridgeSettings()

