from __future__ import annotations

import argparse
import signal
import sys
from pathlib import Path
from typing import Optional

from config_loader import PROJECT_ROOT, ConfigError, load_all_configs
from fleet_server_main import FleetServer


SERVER_CONFIG_PATH = PROJECT_ROOT / "program" / "json" / "server_config.json"


class ServerManager:
    def __init__(self, config_path: Path = SERVER_CONFIG_PATH) -> None:
        self.config_path = config_path
        self.server: Optional[FleetServer] = None
        self.shutdown_requested = False

    def load(self) -> None:
        configs = load_all_configs(self.config_path)
        server_config = configs["server_config"]
        client_info = configs["client_info"]
        control_info = configs["control_info"]

        server = server_config["server"]
        client = client_info["robot_command_client"]
        control = control_info["control_ui"]

        print("========================================")
        print("TurtleBot Fleet Server Manager v0.5")
        print("role: Control UI <-> Fleet Server <-> Robot Command Client")
        print("========================================")
        print(f"project_root: {PROJECT_ROOT}")
        print(f"config: {self.config_path}")
        control_json = control.get("json", {})
        if not isinstance(control_json, dict):
            raise ConfigError("control_info.control_ui.json must be an object")
        control_health = control_json.get("health", {})
        if not isinstance(control_health, dict):
            raise ConfigError("control_info.control_ui.json.health must be an object")
        control_command = control_json.get("command", {})
        if not isinstance(control_command, dict):
            raise ConfigError("control_info.control_ui.json.command must be an object")
        control_data = control_json.get("data_control", {})
        if not isinstance(control_data, dict):
            raise ConfigError("control_info.control_ui.json.data_control must be an object")
        for label, section in {
            "health": control_health,
            "command": control_command,
            "data_control": control_data,
        }.items():
            if "server_port" not in section:
                raise ConfigError(f"control_info.control_ui.json.{label}.server_port is required")

        print(
            "control listen: "
            f"health={server['bind_ip']}:{server['control_health_port']} "
            f"command={server['bind_ip']}:{server['control_command_port']} "
            f"data_control={server['bind_ip']}:{server['control_data_port']}"
        )
        print(
            "control ui: "
            f"{control['ip']} "
            f"health={control_health['server_port']} "
            f"command={control_command['server_port']} "
            f"data_control={control_data['server_port']}"
        )
        print(
            "robot client: "
            f"{client['ip']} "
            f"health={client['health_port']} "
            f"command={client['command_port']} "
            f"data_control={client['data_control_port']}"
        )
        print("run: Ctrl+C to stop")
        print("")

        self.server = FleetServer(self.config_path)

    def run(self) -> None:
        self.load()
        assert self.server is not None
        self.server.run()

    def request_shutdown(self, signum: int, _frame: object) -> None:
        self.shutdown_requested = True
        print(f"\n[MANAGER STOP] signal={signum}")
        raise KeyboardInterrupt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TurtleBot fleet server manager")
    parser.add_argument("--config", default=str(SERVER_CONFIG_PATH), help="Path to server_config.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manager = ServerManager(Path(args.config).resolve())
    signal.signal(signal.SIGTERM, manager.request_shutdown)
    try:
        manager.run()
    except ConfigError as exc:
        print(f"[CONFIG ERROR] {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("[MANAGER STOP] stopped by user")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
