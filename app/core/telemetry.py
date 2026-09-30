from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any


class Telemetry:
    def __init__(self, path: str = "artifacts/telemetry.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, event_type: str, session_id: str, **payload: Any) -> dict[str, Any]:
        event = {
            "timestamp_ms": int(time.time() * 1000),
            "event_type": event_type,
            "session_id": session_id,
            **payload,
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
        return event
