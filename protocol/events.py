from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping
import json

class EventType(str, Enum):
    TASK_CREATED="TASK_CREATED"; AGENT_ASSIGNED="AGENT_ASSIGNED"; WORK_STARTED="WORK_STARTED"
    RESULT_PUBLISHED="RESULT_PUBLISHED"; EVIDENCE_ATTACHED="EVIDENCE_ATTACHED"
    VERIFICATION_REQUESTED="VERIFICATION_REQUESTED"; VERIFIED="VERIFIED"
    CONFLICT_DETECTED="CONFLICT_DETECTED"; PROPOSAL_CREATED="PROPOSAL_CREATED"
    DECISION_REQUIRED="DECISION_REQUIRED"; ACTION_AUTHORIZED="ACTION_AUTHORIZED"
    GITHUB_CHANGE="GITHUB_CHANGE"; REVISION_RECORDED="REVISION_RECORDED"
    ACTION_REJECTED="ACTION_REJECTED"; TASK_BLOCKED="TASK_BLOCKED"

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
    schema_version: str = "0.1"

    def as_dict(self) -> dict[str, Any]:
        return {"event_id":self.event_id,"event_type":self.event_type.value,"task_id":self.task_id,
                "issuer":self.issuer,"correlation_id":self.correlation_id,"idempotency_key":self.idempotency_key,
                "payload":dict(self.payload),"evidence_refs":[dict(x) for x in self.evidence_refs],
                "schema_version":self.schema_version}

    def json(self) -> str:
        return json.dumps(self.as_dict(), sort_keys=True, ensure_ascii=False, separators=(",",":"))
