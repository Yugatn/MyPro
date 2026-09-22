from core.project import EventLog
from core.provenance import ProvenanceNode, ProvenanceStore


def test_provenance_is_persisted_and_linked(tmp_path):
    log = EventLog(tmp_path / "events.jsonl")
    store = ProvenanceStore(tmp_path / "provenance", log)
    node = ProvenanceNode("p1", "probe", (), ("asset",), "mypro")
    digest = store.put(node)
    assert store.read(digest) == node
    assert any(e.event_type == "provenance.link" for e in log.iter_events())
