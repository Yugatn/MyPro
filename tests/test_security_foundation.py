from datetime import datetime, timedelta, timezone

from core.security import Capability, CapabilityStatus, Evidence, EvidenceState, IdentityAnchor, PolicyDecisionKind
from core.security.policy import PolicyEngine, PolicyRequest, audit_decision

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def capability(status=CapabilityStatus.ACTIVE, expires_at=None):
    return Capability("cap_1", "agent:grok", "MODIFY_REPOSITORY", "repo:Yugatn/MyPro", NOW, expires_at, status)


def test_identity_does_not_imply_authority():
    identity = IdentityAnchor("id_1", "agent:grok")
    assert identity.revoked is False
    decision = PolicyEngine().evaluate(PolicyRequest("agent:grok", "MODIFY_REPOSITORY", "repo:Yugatn/MyPro", now=NOW))
    assert decision.kind is PolicyDecisionKind.DENY


def test_revoked_capability_cannot_authorize():
    decision = PolicyEngine().evaluate(PolicyRequest("agent:grok", "MODIFY_REPOSITORY", "repo:Yugatn/MyPro", capability=capability(CapabilityStatus.REVOKED), now=NOW))
    assert decision.kind is PolicyDecisionKind.DENY


def test_expired_capability_cannot_authorize():
    decision = PolicyEngine().evaluate(PolicyRequest("agent:grok", "MODIFY_REPOSITORY", "repo:Yugatn/MyPro", capability=capability(expires_at=NOW - timedelta(seconds=1)), now=NOW))
    assert decision.kind is PolicyDecisionKind.DENY


def test_unverified_evidence_cannot_satisfy_verified_gate():
    evidence = Evidence("ev_1", EvidenceState.OBSERVED, "agent:grok", ("event:1",), NOW)
    decision = PolicyEngine().evaluate(PolicyRequest("agent:grok", "MODIFY_REPOSITORY", "repo:Yugatn/MyPro", capability=capability(), evidence=(evidence,), require_verified_evidence=True, now=NOW))
    assert decision.kind is PolicyDecisionKind.REQUIRE_VERIFICATION


def test_verified_evidence_allows_and_is_auditable():
    evidence = Evidence("ev_2", EvidenceState.VERIFIED, "independent-verifier", ("event:1", "verification:2"), NOW)
    decision = PolicyEngine().evaluate(PolicyRequest("agent:grok", "MODIFY_REPOSITORY", "repo:Yugatn/MyPro", capability=capability(), evidence=(evidence,), require_verified_evidence=True, now=NOW))
    assert decision.kind is PolicyDecisionKind.ALLOW
    audit = audit_decision(decision=decision, action="MODIFY_REPOSITORY", subject_id="agent:grok")
    assert audit.decision_id == decision.decision_id
    assert audit.evidence_refs == ("ev_2",)
