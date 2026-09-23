from __future__ import annotations
from .events import EventEnvelope

class EventLog:
    """Append-only, idempotent event store. Persistence is intentionally injectable."""
    def __init__(self) -> None:
        self._events: list[EventEnvelope] = []
        self._keys: set[str] = set()

    def append(self, event: EventEnvelope) -> bool:
        if event.idempotency_key in self._keys or event.event_id in {e.event_id for e in self._events}:
            return False
        self._events.append(event); self._keys.add(event.idempotency_key); return True

    def all(self) -> tuple[EventEnvelope, ...]: return tuple(self._events)
    def for_task(self, task_id: str) -> tuple[EventEnvelope, ...]:
        return tuple(e for e in self._events if e.task_id == task_id)
