from __future__ import annotations

from .events import EventEnvelope


class EventConflict(ValueError):
    """Raised when an event id or idempotency key is reused for different content."""


class EventLog:
    """Append-only event store with deterministic duplicate detection."""

    def __init__(self) -> None:
        self._events: list[EventEnvelope] = []
        self._by_id: dict[str, EventEnvelope] = {}
        self._by_key: dict[str, EventEnvelope] = {}

    def append(self, event: EventEnvelope) -> bool:
        existing_id = self._by_id.get(event.event_id)
        existing_key = self._by_key.get(event.idempotency_key)

        if existing_id is not None or existing_key is not None:
            existing = existing_id or existing_key
            if existing is not None and existing.canonical_json() != event.canonical_json():
                raise EventConflict(
                    "event_id or idempotency_key already belongs to different content"
                )
            return False

        self._events.append(event)
        self._by_id[event.event_id] = event
        self._by_key[event.idempotency_key] = event
        return True

    def all(self) -> tuple[EventEnvelope, ...]:
        return tuple(self._events)

    def for_task(self, task_id: str) -> tuple[EventEnvelope, ...]:
        return tuple(e for e in self._events if e.task_id == task_id)

    def contains(self, event_id: str) -> bool:
        return event_id in self._by_id
