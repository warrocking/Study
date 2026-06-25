from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from fleet_protocol import load_json_file


class OpenCVManager:
    """Read OpenCV safety events without owning camera/UI code."""

    def __init__(self, event_file: str | Path) -> None:
        self.event_file = Path(event_file)

    def latest_event(self) -> Dict[str, Any]:
        if not self.event_file.exists():
            return {"lv": "NORMAL", "source": "opencv_manager", "exists": False}
        return load_json_file(self.event_file, {"lv": "NORMAL"})
