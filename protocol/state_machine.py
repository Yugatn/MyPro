from __future__ import annotations

from enum import Enum

from .events import EventEnvelope, EventType


class ProtocolState(str, Enum):
    NEW = "NEW"
    ASSIGNED = "ASSIGNED"
    RUNNING = "RUNNING"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    VERIFIED = "VERIFIED"
    CONFLICT = "CONFLICT"
    PROPOSAL = "PROPOSAL"
    DECISION = "DECISION"
    ACTION_READY = "ACTION_READY"
    CHANGED = "CHANGED"
    BLOCKED = "BLOCKED"


_ALLOWED: dict[ProtocolState, set[EventType]] = {
    ProtocolState.NEW: {EventType.AGENT_ASSIGNED, EventType.TASK_BLOCKED},
    ProtocolState.ASSIGNED: {EventType.WORK_STARTED, EventType.TASK_BLOCKED},
    ProtocolState.RUNNING: {
        EventType.RESULT_PUBLISHED,
        EventType.EVIDENCE_ATTACHED,
        EventType.TASK_BLOCKED,
    },
    ProtocolState.PENDING_VERIFICATION: {
        EventType.EVIDENCE_ATTACHED,
        EventType.VERIFICATION_REQUESTED,
        EventType.VERIFIED,
        EventType.CONFLICT_DETECTED,
        EventType.TASK_BLOCKED,
    },
    ProtocolState.VERIFIED: {EventType.PROPOSAL_CREATED, EventType.EVIDENCE_ATTACHED},
    ProtocolState.CONFLICT: {
        EventType.VERIFICATION_REQUESTED,
        EventType.DECISION_REQUIRED,
        EventType.TASK_BLOCKED,
    },
    ProtocolState.PROPOSAL: {EventType.DECISION_REQUIRED, EventType.TASK_BLOCKED},
    ProtocolState.DECISION: {
        EventType.ACTION_AUTHORIZED,
        EventType.ACTION_REJECTED,
        EventType.TASK_BLOCKED,
    },
    ProtocolState.ACTION_READY: {
        EventType.GITHUB_CHANGE,
        EventType.ACTION_REJECTED,
        EventType.TASK_BLOCKED,
    },
    ProtocolState.CHANGED: {EventType.REVISION_RECORDED},
}


_TRANSITIONS: dict[EventType, ProtocolState] = {
    EventType.AGENT_ASSIGNED: ProtocolState.ASSIGNED,
    EventType.WORK_STARTED: ProtocolState.RUNNING,
    EventType.RESULT_PUBLISHED: ProtocolState.PENDING_VERIFICATION,
    EventType.EVIDENCE_ATTACHED: ProtocolState.PENDING_VERIFICATION,
    EventType.VERIFICATION_REQUESTED: ProtocolState.PENDING_VERIFICATION,
    EventType.VERIFIED: ProtocolState.VERIFIED,
    EventType.CONFLICT_DETECTED: ProtocolState.CONFLICT,
    EventType.PROPOSAL_CREATED: ProtocolState.PROPOSAL,
    EventType.DECISION_REQUIRED: ProtocolState.DECISION,
    EventType.ACTION_AUTHORIZED: ProtocolState.ACTION_READY,
    EventType.GITHUB_CHANGE: ProtocolState.CHANGED,
    EventType.REVISION_RECORDED: ProtocolState.CHANGED,
    EventType.ACTION_REJECTED: ProtocolState.BLOCKED,
    EventType.TASK_BLOCKED: ProtocolState.BLOCKED,
}


def apply(state: ProtocolState, event: EventEnvelope) -> ProtocolState:
    allowed = _ALLOWED.get(state, set())
    if event.event_type not in allowed:
        raise ValueError(
            f"invalid transition: {state.value} + {event.event_type.value}"
        )
    return _TRANSITIONS[event.event_type]
