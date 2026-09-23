from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Mapping


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class CapabilityStatus(str, Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class EvidenceState(str, Enum):
    CLAIMED = "claimed"
    OBSERVED = "observed"
    VERIFIED = "verified"
    CONTRADICTED = "contradicted"
    STALE = "stale"
    UNKNOWN = "unknown"


class PolicyDecisionKind(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_VERIFICATION = "REQUIRE_VERIFICATION"
    REQUIRE_HUMAN_DECISION = "REQUIRE_HUMAN_DECISION"
    DEFER = "DEFER"


@dataclass(frozen=True)
class Subject:
    subject_id: str
    kind: str
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class IdentityAnchor:
    identity_id: str
    subject_id: str
    version: int = 1
    provenance: tuple[str, ...] = ()
    revoked: bool = False

    def __post_init__(self) -> None:
        if not self.identity_id or not self.subject_id:
            raise ValueError("identity_id and subject_id are required")
        if self.version < 1:
            raise ValueError("version must be >= 1")


@dataclass(frozen=True)
class Capability:
    capability_id: str
    subject_id: str
    operation: str
    resource: str
    issued_at: datetime
    expires_at: datetime | None = None
    status: CapabilityStatus = CapabilityStatus.ACTIVE
    parent_id: str | None = None

    def is_active(self, now: datetime | None = None) -> bool:
        now = now or utc_now()
        return self.status is CapabilityStatus.ACTIVE and (
            self.expires_at is None or now < self.expires_at
        )

    def permits(self, subject_id: str, operation: str, resource: str, now: datetime | None = None) -> bool:
        return (
            self.subject_id == subject_id
            and self.operation == operation
            and self.resource == resource
            and self.is_active(now)
        )


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    state: EvidenceState
    source: str
    provenance: tuple[str, ...]
    observed_at: datetime
    content_hash: str | None = None

    def is_verified(self) -> bool:
        return self.state is EvidenceState.VERIFIED and bool(self.provenance)


@dataclass(frozen=True)
class PolicyDecision:
    decision_id: str
    kind: PolicyDecisionKind
    policy_id: str
    policy_version: str
    reason_codes: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    evaluated_at: datetime
    audit_ref: str | None = None


@dataclass(frozen=True)
class AuditRecord:
    audit_id: str
    action: str
    subject_id: str
    decision_id: str
    outcome: PolicyDecisionKind
    created_at: datetime
    evidence_refs: tuple[str, ...] = ()
    metadata: Mapping[str, str] = field(default_factory=dict)
