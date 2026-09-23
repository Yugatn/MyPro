from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping
from uuid import uuid4

from .models import (
    AuditRecord,
    Capability,
    Evidence,
    PolicyDecision,
    PolicyDecisionKind,
    utc_now,
)


@dataclass(frozen=True)
class PolicyRequest:
    subject_id: str
    operation: str
    resource: str
    capability: Capability | None = None
    evidence: tuple[Evidence, ...] = ()
    require_verified_evidence: bool = False
    now: datetime | None = None


class PolicyEngine:
    """Deterministic authorization kernel; it evaluates but never executes."""

    POLICY_ID = "symbiont.foundation.authorization"
    POLICY_VERSION = "0.1"

    def evaluate(self, request: PolicyRequest) -> PolicyDecision:
        now = request.now or utc_now()
        refs = tuple(e.evidence_id for e in request.evidence)
        if request.capability is None:
            return self._decision(PolicyDecisionKind.DENY, "CAPABILITY_REQUIRED", refs, now)
        if not request.capability.permits(request.subject_id, request.operation, request.resource, now):
            reason = (
                "CAPABILITY_EXPIRED_OR_REVOKED"
                if not request.capability.is_active(now)
                else "CAPABILITY_SCOPE_MISMATCH"
            )
            return self._decision(PolicyDecisionKind.DENY, reason, refs, now)
        if request.require_verified_evidence and not any(e.is_verified() for e in request.evidence):
            return self._decision(
                PolicyDecisionKind.REQUIRE_VERIFICATION,
                "VERIFIED_EVIDENCE_REQUIRED",
                refs,
                now,
            )
        return self._decision(PolicyDecisionKind.ALLOW, "AUTHORIZED", refs, now)

    def _decision(self, kind: PolicyDecisionKind, reason: str, refs: tuple[str, ...], now: datetime) -> PolicyDecision:
        return PolicyDecision(
            decision_id=f"dec_{uuid4().hex}",
            kind=kind,
            policy_id=self.POLICY_ID,
            policy_version=self.POLICY_VERSION,
            reason_codes=(reason,),
            evidence_refs=refs,
            evaluated_at=now,
        )


def audit_decision(*, decision: PolicyDecision, action: str, subject_id: str, metadata: Mapping[str, str] | None = None) -> AuditRecord:
    return AuditRecord(
        audit_id=f"audit_{uuid4().hex}",
        action=action,
        subject_id=subject_id,
        decision_id=decision.decision_id,
        outcome=decision.kind,
        created_at=decision.evaluated_at,
        evidence_refs=decision.evidence_refs,
        metadata=metadata or {},
    )
