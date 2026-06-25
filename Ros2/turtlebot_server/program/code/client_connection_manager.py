from __future__ import annotations

from typing import Any, Dict


class ClientConnectionManager:
    """Describe the v0.5 Robot Command Client TCP boundary."""

    def __init__(
        self,
        client_ip: str,
        health_port: int,
        command_port: int,
        data_control_port: int,
    ) -> None:
        self.client_ip = client_ip
        self.health_port = health_port
        self.command_port = command_port
        self.data_control_port = data_control_port

    def describe(self) -> Dict[str, Any]:
        return {
            "component": "client_connection_manager",
            "client_ip": self.client_ip,
            "health_port": self.health_port,
            "command_port": self.command_port,
            "data_control_port": self.data_control_port,
            "health_outbound_messages": [
                "client_heartbeat_request",
            ],
            "command_outbound_messages": [
                "server_command",
            ],
            "health_expected_inbound_messages": [
                "client_heartbeat_response",
            ],
            "command_expected_inbound_messages": [
                "agent_result",
            ],
            "active_runtime_owner": "fleet_server_main.FleetServer",
        }
