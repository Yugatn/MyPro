from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Any

from protocol.event_log import EventConflict, EventLog
from protocol.events import EventEnvelope, EventType
from protocol.state_machine import ProtocolState, apply
from protocol.validation import validate_event


@dataclass
class AgentProtocolRuntime:
    """Deterministic event runtime; side effects stay behind explicit adapters."""

    log: EventLog
    state: dict[str, ProtocolState]
    _last_result: dict[str, str] = field(default_factory=dict)

    @classmethod
    def create(cls) -> "AgentProtocolRuntime":
        return cls(log=EventLog(), state={})

    def ingest(self, event: EventEnvelope) -> ProtocolState:
        validate_event(event)

        existing = self.log.get(event.event_id)
        if existing is not None:
            if existing.canonical_json() != event.canonical_json():
                raise EventConflict("event_id already exists with different content")
            return self.state[event.task_id]

        current = self.state.get(event.task_id)
        if current is None:
            if event.event_type is not EventType.TASK_CREATED:
                raise ValueError("first event must be TASK_CREATED")
            next_state = ProtocolState.NEW
        else:
            next_state = apply(current, event)

        # Append first: if an idempotency conflict is detected, in-memory state
        # remains unchanged.
        self.log.append(event)
        self.state[event.task_id] = next_state

        if event.event_type is EventType.RESULT_PUBLISHED:
            self._last_result[event.task_id] = str(event.payload["result_id"])

        return next_state

    def make_event(
        self,
        *,
        event_type: EventType,
        task_id: str,
        issuer: str,
        correlation_id: str,
        payload: dict[str, Any],
        evidence_refs: tuple[dict[str, Any], ...] = (),
    ) -> EventEnvelope:
        material = {
            "event_type": event_type.value,
            "task_id": task_id,
            "issuer": issuer,
            "correlation_id": correlation_id,
            "payload": payload,
            "evidence_refs": evidence_refs,
            "schema_version": "0.2",
        }
        canonical = json.dumps(
            material, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        digest = sha256(canonical.encode("utf-8")).hexdigest()
        return EventEnvelope(
            event_id=f"evt_{digest}",
            event_type=event_type,
            task_id=task_id,
            issuer=issuer,
            correlation_id=correlation_id,
            idempotency_key=f"idem_{digest}",
            payload=payload,
            evidence_refs=evidence_refs,
            schema_version="0.2",
        )
