from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class Trace:
    trace_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    events: list[dict] = field(default_factory=list)

    def add(self, stage: str, payload: dict) -> None:
        self.events.append({"stage": stage, "payload": payload})

    def to_dict(self) -> dict:
        return {"trace_id": self.trace_id, "created_at": self.created_at, "events": self.events}
