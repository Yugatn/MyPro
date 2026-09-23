from __future__ import annotations

from .events import EventEnvelope, EventType


class ProtocolViolation(ValueError):
    """Raised when an event violates a protocol invariant."""


def _required(payload: dict, *keys: str) -> None:
    missing = [key for key in keys if not payload.get(key)]
    if missing:
        raise ProtocolViolation(f"missing required payload fields: {', '.join(missing)}")


def validate_event(event: EventEnvelope) -> None:
    if not event.event_id or not event.task_id or not event.issuer:
        raise ProtocolViolation("event identity fields are required")
    if not event.correlation_id or not event.idempotency_key:
        raise ProtocolViolation("correlation_id and idempotency_key are required")
    if event.schema_version != "0.2":
        raise ProtocolViolation("unsupported schema version")

    payload = dict(event.payload)

    if event.event_type is EventType.TASK_CREATED:
        _required(payload, "task_kind")

    elif event.event_type is EventType.AGENT_ASSIGNED:
        _required(payload, "agent")

    elif event.event_type is EventType.RESULT_PUBLISHED:
        _required(payload, "result_id", "verification_state")
        if payload["verification_state"] not in {"claimed", "observed"}:
            raise ProtocolViolation("RESULT_PUBLISHED must be claimed or observed")

    elif event.event_type is EventType.EVIDENCE_ATTACHED:
        _required(payload, "evidence_id", "evidence_state")
        if payload["evidence_state"] not in {"claimed", "observed", "verified"}:
            raise ProtocolViolation("invalid evidence_state")

    elif event.event_type is EventType.VERIFIED:
        _required(payload, "verification_id", "verifier", "verification_state")
        if payload["verification_state"] != "independent":
            raise ProtocolViolation("VERIFIED requires independent verification")
        if payload["verifier"] == event.issuer:
            raise ProtocolViolation("verifier must be distinct from event issuer")

    elif event.event_type is EventType.PROPOSAL_CREATED:
        _required(payload, "proposal_id", "verification_state")
        if payload["verification_state"] != "verified":
            raise ProtocolViolation("PROPOSAL_CREATED requires verified evidence")

    elif event.event_type is EventType.DECISION_REQUIRED:
        _required(payload, "decision_id")

    elif event.event_type is EventType.ACTION_AUTHORIZED:
        _required(payload, "authorization_id", "authorized_by", "decision_id")

    elif event.event_type is EventType.GITHUB_CHANGE:
        _required(payload, "authorization_id", "change_id", "repository", "changes")
        if not isinstance(payload["changes"], list) or not payload["changes"]:
            raise ProtocolViolation("GITHUB_CHANGE requires a non-empty changes list")

    elif event.event_type is EventType.REVISION_RECORDED:
        _required(payload, "revision_id", "change_id")

    elif event.event_type is EventType.ACTION_REJECTED:
        _required(payload, "decision_id", "reason")
