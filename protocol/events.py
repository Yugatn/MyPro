from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import json
from types import MappingProxyType
from typing import Any, Mapping


def _freeze_json(value: Any) -> Any:
    """Snapshot JSON-like values and recursively prevent subsequent mutation."""
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise TypeError("event payload keys must be strings")
        return MappingProxyType({key: _freeze_json(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_json(item) for item in value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"unsupported event payload type: {type(value).__name__}")


def _thaw_json(value: Any) -> Any:
    """Create JSON-compatible copies without exposing the internal snapshot."""
    if isinstance(value, Mapping):
        return {key: _thaw_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


class EventType(str, Enum):
    TASK_CREATED = "TASK_CREATED"
    AGENT_ASSIGNED = "AGENT_ASSIGNED"
    WORK_STARTED = "WORK_STARTED"
    RESULT_PUBLISHED = "RESULT_PUBLISHED"
    EVIDENCE_ATTACHED = "EVIDENCE_ATTACHED"
    VERIFICATION_REQUESTED = "VERIFICATION_REQUESTED"
    VERIFIED = "VERIFIED"
    CONFLICT_DETECTED = "CONFLICT_DETECTED"
    PROPOSAL_CREATED = "PROPOSAL_CREATED"
    DECISION_REQUIRED = "DECISION_REQUIRED"
    ACTION_AUTHORIZED = "ACTION_AUTHORIZED"
    GITHUB_CHANGE = "GITHUB_CHANGE"
    REVISION_RECORDED = "REVISION_RECORDED"
    ACTION_REJECTED = "ACTION_REJECTED"
    TASK_BLOCKED = "TASK_BLOCKED"


@dataclass(frozen=True)
class EventEnvelope:
    event_id: str
    event_type: EventType
    task_id: str
    issuer: str
    correlation_id: str
    idempotency_key: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    evidence_refs: tuple[Mapping[str, Any], ...] = ()
    schema_version: str = "0.2"

    def __post_init__(self) -> None:
        # A frozen dataclass does not freeze nested dictionaries/lists.
        # Snapshot at construction so caller-owned payloads cannot rewrite history.
        object.__setattr__(self, "payload", _freeze_json(self.payload))
        object.__setattr__(
            self, "evidence_refs", tuple(_freeze_json(item) for item in self.evidence_refs)
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "task_id": self.task_id,
            "issuer": self.issuer,
            "correlation_id": self.correlation_id,
            "idempotency_key": self.idempotency_key,
            "payload": _thaw_json(self.payload),
            "evidence_refs": [_thaw_json(x) for x in self.evidence_refs],
            "schema_version": self.schema_version,
        }

    def canonical_json(self) -> str:
        return json.dumps(
            self.as_dict(),
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    def json(self) -> str:
        return self.canonical_json()
