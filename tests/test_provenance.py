from core.provenance import ProvenanceNode, verify_provenance


def test_provenance_parent_chain():
    first = ProvenanceNode("p1", "probe", (), ("asset",), "mypro")
    second = ProvenanceNode("p2", "analysis", ("asset",), ("obs",), "mypro", parent_ids=("p1",))
    assert first.content_hash != second.content_hash
    assert verify_provenance({"p1": first, "p2": second})


def test_missing_parent_is_invalid():
    node = ProvenanceNode("p2", "analysis", (), ("obs",), "mypro", parent_ids=("missing",))
    assert not verify_provenance({"p2": node})
