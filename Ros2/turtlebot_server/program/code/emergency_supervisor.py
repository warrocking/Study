from __future__ import annotations

from typing import Any, Dict, Iterable


class EmergencySupervisor:
    """Small policy helper for emergency command allowance."""

    def __init__(self, allowed_during_emergency: Iterable[str] | None = None) -> None:
        self.allowed_during_emergency = set(allowed_during_emergency or {
            "status_request",
            "robot_state_request",
            "job_status_request",
            "clear_emergency",
            "reset_all_jobs",
            "emergency_stop",
            "all_stop",
        })

    def command_allowed(self, action: str, global_state: str) -> bool:
        if global_state != "EMERGENCY":
            return True
        return action in self.allowed_during_emergency

    def describe(self) -> Dict[str, Any]:
        return {
            "component": "emergency_supervisor",
            "allowed_during_emergency": sorted(self.allowed_during_emergency),
        }
