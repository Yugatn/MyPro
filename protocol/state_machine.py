from __future__ import annotations
from enum import Enum
from .events import EventType, EventEnvelope

class ProtocolState(str, Enum):
    NEW="NEW"; ASSIGNED="ASSIGNED"; RUNNING="RUNNING"; PENDING_VERIFICATION="PENDING_VERIFICATION"
    VERIFIED="VERIFIED"; CONFLICT="CONFLICT"; PROPOSAL="PROPOSAL"; DECISION="DECISION"
    ACTION_READY="ACTION_READY"; CHANGED="CHANGED"; BLOCKED="BLOCKED"

_ALLOWED={
 ProtocolState.NEW:{EventType.TASK_CREATED,EventType.AGENT_ASSIGNED},
 ProtocolState.ASSIGNED:{EventType.WORK_STARTED,EventType.TASK_BLOCKED},
 ProtocolState.RUNNING:{EventType.RESULT_PUBLISHED,EventType.TASK_BLOCKED},
 ProtocolState.PENDING_VERIFICATION:{EventType.VERIFICATION_REQUESTED,EventType.VERIFIED,EventType.CONFLICT_DETECTED},
 ProtocolState.VERIFIED:{EventType.PROPOSAL_CREATED},
 ProtocolState.CONFLICT:{EventType.VERIFICATION_REQUESTED,EventType.TASK_BLOCKED,EventType.DECISION_REQUIRED},
 ProtocolState.PROPOSAL:{EventType.DECISION_REQUIRED},
 ProtocolState.DECISION:{EventType.ACTION_AUTHORIZED,EventType.ACTION_REJECTED},
 ProtocolState.ACTION_READY:{EventType.GITHUB_CHANGE,EventType.ACTION_REJECTED},
 ProtocolState.CHANGED:{EventType.REVISION_RECORDED},
}
_TRANS={
 EventType.TASK_CREATED:ProtocolState.NEW, EventType.AGENT_ASSIGNED:ProtocolState.ASSIGNED,
 EventType.WORK_STARTED:ProtocolState.RUNNING, EventType.RESULT_PUBLISHED:ProtocolState.PENDING_VERIFICATION,
 EventType.VERIFICATION_REQUESTED:ProtocolState.PENDING_VERIFICATION, EventType.VERIFIED:ProtocolState.VERIFIED,
 EventType.CONFLICT_DETECTED:ProtocolState.CONFLICT, EventType.PROPOSAL_CREATED:ProtocolState.PROPOSAL,
 EventType.DECISION_REQUIRED:ProtocolState.DECISION, EventType.ACTION_AUTHORIZED:ProtocolState.ACTION_READY,
 EventType.GITHUB_CHANGE:ProtocolState.CHANGED, EventType.REVISION_RECORDED:ProtocolState.CHANGED,
 EventType.ACTION_REJECTED:ProtocolState.BLOCKED, EventType.TASK_BLOCKED:ProtocolState.BLOCKED,
}

def apply(state: ProtocolState, event: EventEnvelope) -> ProtocolState:
    if event.event_type not in _ALLOWED.get(state,set()):
        raise ValueError(f"invalid transition: {state.value} + {event.event_type.value}")
    return _TRANS[event.event_type]
