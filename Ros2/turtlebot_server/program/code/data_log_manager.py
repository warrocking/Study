from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


class DataLogManager:
    """Describe the v0.5 log boundary used by FleetServer."""

    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir)

    def describe(self) -> Dict[str, Any]:
        return {
            "component": "data_log_manager",
            "base_dir": str(self.base_dir),
            "active_runtime_owner": "fleet_protocol.save_json_log",
            "log_policy": "history file plus latest file per category",
        }
