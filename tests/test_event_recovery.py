import pytest
from core.errors import EventLogCorrupt
from core.project import EventLog, ProjectEvent


def test_partial_tail_is_recovered(tmp_path):
    path = tmp_path / "events.jsonl"
    log = EventLog(path)
    log.append(ProjectEvent("1", "a", {}))
    with path.open("ab") as handle:
        handle.write(b'{"event_id":"broken"')
    recovered = EventLog(path)
    assert recovered.count == 1
    assert recovered.tip_hash == log.tip_hash


def test_chain_corruption_is_rejected(tmp_path):
    path = tmp_path / "events.jsonl"
    log = EventLog(path)
    log.append(ProjectEvent("1", "a", {}))
    raw = path.read_text()
    path.write_text(raw.replace('"a"', '"tampered"'))
    with pytest.raises(EventLogCorrupt):
        EventLog(path)
