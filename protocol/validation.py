from __future__ import annotations
from .events import EventEnvelope, EventType

class ProtocolViolation(ValueError): pass

_TERMINAL_GATES={EventType.GITHUB_CHANGE, EventType.REVISION_RECORDED}

def validate_event(event: EventEnvelope) -> None:
    if not event.event_id or not event.task_id or not event.issuer or not event.idempotency_key:
        raise ProtocolViolation("event identity fields are required")
    if event.schema_version != "0.1": raise ProtocolViolation("unsupported schema version")
    if event.event_type is EventType.VERIFIED and event.payload.get("verification_state") != "independent":
        raise ProtocolViolation("VERIFIED requires independent verification")
    if event.event_type is EventType.PROPOSAL_CREATED and event.payload.get("verification_state") != "verified":
        raise ProtocolViolation("PROPOSAL_CREATED requires verified evidence")
    if event.event_type is EventType.GITHUB_CHANGE and not event.payload.get("authorized"):
        raise ProtocolViolation("GITHUB_CHANGE requires explicit authorization")
