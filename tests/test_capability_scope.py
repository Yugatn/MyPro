import pytest
from core.capability import CapabilityIssuer, Operation, scope_covers, scope_matches
from core.errors import CapabilityDenied


def test_scope_matching():
    assert scope_matches("*", "media:blake3:abc")
    assert scope_matches("media:*", "media:blake3:abc")
    assert scope_matches("project:p1", "project:p1")
    assert not scope_matches("project:p1", "project:p2")
    assert not scope_matches("project:p1", "project:p1:analysis")


def test_scope_coverage():
    assert scope_covers("*", "media:*")
    assert scope_covers("media:*", "media:blake3:abc")
    assert not scope_covers("media:blake3:abc", "media:*")


def test_delegation_cannot_amplify():
    issuer = CapabilityIssuer()
    parent = issuer.issue(subject="agent", operations=[Operation.MEDIA_READ],
                          resource_scope="media:*", ttl_seconds=60, delegable=True)
    with pytest.raises(CapabilityDenied):
        issuer.issue(subject="child", operations=[Operation.MEDIA_READ],
                     resource_scope="*", ttl_seconds=60, parent=parent.id)
