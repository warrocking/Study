from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[2]
JSON_DIR = PROJECT_ROOT / "program" / "json"


class ConfigError(RuntimeError):
    pass


def load_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError as exc:
        raise ConfigError(f"missing config file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"invalid JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"config root must be an object: {path}")
    return data


def require_keys(data: Dict[str, Any], keys: Iterable[str], label: str) -> None:
    missing = [key for key in keys if key not in data]
    if missing:
        raise ConfigError(f"{label} missing keys: {', '.join(missing)}")


def ensure_directories(server_config: Dict[str, Any]) -> None:
    paths = server_config.get("paths", {})
    if not isinstance(paths, dict):
        raise ConfigError("server_config.paths must be an object")

    for key, value in paths.items():
        if not key.endswith("_dir") and key not in {"project_root", "program_dir", "code_dir", "json_dir", "data_dir"}:
            continue
        if not isinstance(value, str) or not value:
            raise ConfigError(f"server_config.paths.{key} must be a non-empty string")
        Path(value).mkdir(parents=True, exist_ok=True)


def load_all_configs(config_path: Path | None = None) -> Dict[str, Dict[str, Any]]:
    server_config_path = config_path or JSON_DIR / "server_config.json"
    server_config = load_json(server_config_path)
    require_keys(server_config, ["server", "files", "paths"], "server_config")

    files = server_config.get("files", {})
    if not isinstance(files, dict):
        raise ConfigError("server_config.files must be an object")

    def file_path(key: str) -> Path:
        raw = files.get(key)
        if not isinstance(raw, str) or not raw.strip():
            raise ConfigError(f"server_config.files.{key} is required")
        path = Path(str(raw))
        return path if path.is_absolute() else PROJECT_ROOT / path

    configs = {
        "server_config": server_config,
        "client_info": load_json(file_path("client_info_file")),
        "control_info": load_json(file_path("control_info_file")),
        "emergency_info": load_json(file_path("emergency_info_file")),
    }

    ensure_directories(server_config)
    validate_ports(configs)
    return configs


def validate_ports(configs: Dict[str, Dict[str, Any]]) -> None:
    server_config = configs["server_config"]
    client_info = configs["client_info"]

    server = server_config.get("server", {})
    if not isinstance(server, dict):
        raise ConfigError("server_config.server must be an object")
    for key in ("control_port", "control_health_port", "control_command_port", "control_data_port"):
        if key not in server:
            raise ConfigError(f"server_config.server.{key} is required")
    control_ports = {
        "control_port": int(server["control_port"]),
        "control_health_port": int(server["control_health_port"]),
        "control_command_port": int(server["control_command_port"]),
        "control_data_port": int(server["control_data_port"]),
    }
    client = client_info.get("robot_command_client", {})
    if not isinstance(client, dict):
        raise ConfigError("client_info.robot_command_client must be an object")
    for key in ("health_port", "command_port", "data_control_port"):
        if key not in client:
            raise ConfigError(f"client_info.robot_command_client.{key} is required")
    client_ports = {
        "health_port": int(client["health_port"]),
        "command_port": int(client["command_port"]),
        "data_control_port": int(client["data_control_port"]),
    }
    for key, value in control_ports.items():
        if not (1 <= value <= 65535):
            raise ConfigError(f"invalid server {key}: {value}")
    for key, value in client_ports.items():
        if not (1 <= value <= 65535):
            raise ConfigError(f"invalid client {key}: {value}")
