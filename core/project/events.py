"""Append-only event primitives for the MyPro project log."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProjectEvent:
    event_id: str
    event_type: str
    payload: dict[str, Any]
    schema_version: str = "0.2"
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.created_at:
            object.__setattr__(
                self,
                "created_at",
                datetime.now(timezone.utc).isoformat(),
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "payload": self.payload,
            "schema_version": self.schema_version,
            "created_at": self.created_at,
        }


class EventLog:
    """Minimal append-only JSONL event store.

    This class deliberately does not expose mutation of existing records.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def append(self, event: ProjectEvent) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(event.to_dict(), ensure_ascii=False, sort_keys=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
            handle.flush()

    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
