from __future__ import annotations

from typing import Any, Dict


class CommandRouter:
    """Describe the v0.5 routing boundary used by FleetServer.

    FleetServer currently owns the executable routing path. This class is kept as
    the future extraction point for policy lookup, target resolution, priority
    checks, queue decisions, and all_stop fan-out.
    """

    def describe(self) -> Dict[str, Any]:
        return {
            "component": "command_router",
            "active_runtime_owner": "fleet_server_main.FleetServer",
            "planned_responsibilities": [
                "action_policy lookup",
                "target resolution",
                "priority and interrupt policy checks",
                "queue decision",
                "all_stop fanout",
            ],
        }
