from __future__ import annotations

from typing import Any, Dict


class ControlConnectionManager:
    """Describe the v0.5 Control UI TCP boundary.

    Control UI uses the server public IP and control port from server_config.json.
    The active socket loop is still owned by FleetServer.
    """

    def __init__(self, bind_ip: str, health_port: int, command_port: int, data_control_port: int) -> None:
        self.bind_ip = bind_ip
        self.health_port = health_port
        self.command_port = command_port
        self.data_control_port = data_control_port

    def describe(self) -> Dict[str, Any]:
        return {
            "component": "control_connection_manager",
            "bind_ip": self.bind_ip,
            "health_port": self.health_port,
            "command_port": self.command_port,
            "data_control_port": self.data_control_port,
            "supported_messages": [
                "control_health_request",
                "operator_request",
                "control_command_request",
                "control_data_request",
            ],
            "active_runtime_owner": "fleet_server_main.FleetServer",
        }
