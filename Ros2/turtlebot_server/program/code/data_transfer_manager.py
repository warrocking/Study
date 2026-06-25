from __future__ import annotations

from typing import Any, Dict


class DataTransferManager:
    """Describe the v0.5 data transfer boundary used by FleetServer."""

    def describe(self) -> Dict[str, Any]:
        return {
            "component": "data_transfer_manager",
            "active_runtime_owner": "fleet_server_main.FleetServer",
            "supported_methods": ["rsync_over_ssh"],
            "supported_initial_data_types": ["image", "log"],
        }
