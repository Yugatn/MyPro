import pytest

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


def test_public_security_api_imports():
    # Regression: the package previously exported no domain objects.
    assert Capability.__module__ == "core.security.models"
    assert PolicyEngine.__module__ == "core.security.policy"


def test_capability_not_valid_before_issue_time():
    decision = PolicyEngine().evaluate(
        PolicyRequest(
            "agent:grok", "MODIFY_REPOSITORY", "repo:Yugatn/MyPro",
            capability=capability(), now=NOW - timedelta(seconds=1),
        )
    )
    assert decision.kind is PolicyDecisionKind.DENY


def test_scope_mismatches_are_denied():
    for subject, operation, resource in [
        ("agent:unknown", "MODIFY_REPOSITORY", "repo:Yugatn/MyPro"),
        ("agent:grok", "READ_CONTEXT", "repo:Yugatn/MyPro"),
        ("agent:grok", "MODIFY_REPOSITORY", "repo:another/project"),
    ]:
        decision = PolicyEngine().evaluate(
            PolicyRequest(subject, operation, resource, capability=capability(), now=NOW)
        )
        assert decision.kind is PolicyDecisionKind.DENY


def test_naive_timestamps_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        Capability("cap", "subject", "READ_CONTEXT", "repo", datetime(2026, 1, 1))
    with pytest.raises(ValueError, match="timezone-aware"):
        capability(expires_at=datetime(2026, 2, 1))
    with pytest.raises(ValueError, match="timezone-aware"):
        capability().is_active(datetime(2026, 2, 1))


def test_invalid_expiry_order_rejected():
    with pytest.raises(ValueError, match="follow issued_at"):
        capability(expires_at=NOW)


@pytest.mark.parametrize("state", [EvidenceState.CLAIMED, EvidenceState.OBSERVED,
                                  EvidenceState.CONTRADICTED, EvidenceState.STALE,
                                  EvidenceState.UNKNOWN])
def test_unverified_states_cannot_pass_evidence_gate(state):
    evidence = Evidence("ev", state, "agent:grok", ("record:1",), NOW)
    decision = PolicyEngine().evaluate(
        PolicyRequest("agent:grok", "MODIFY_REPOSITORY", "repo:Yugatn/MyPro",
                      capability=capability(), evidence=(evidence,),
                      require_verified_evidence=True, now=NOW)
    )
    assert decision.kind is PolicyDecisionKind.REQUIRE_VERIFICATION
