from pathlib import Path
import pytest
from core.project.events import EventLog, EventLogCorrupt, SnapshotStore

def test_chain_and_reopen(tmp_path:Path):
    p=tmp_path/"events.jsonl"; log=EventLog(p)
    a=log.append(type="a",payload={"x":1}); b=log.append(type="b",payload={"y":2})
    assert b.prev_hash==a.event_hash
    assert EventLog(p).tip_hash==b.event_hash

def test_tamper_detected(tmp_path:Path):
    p=tmp_path/"events.jsonl"; log=EventLog(p); log.append(type="a",payload={"x":1})
    raw=p.read_text().replace('"x":1','"x":2'); p.write_text(raw)
    with pytest.raises(EventLogCorrupt): list(EventLog(p).iter_events())

def test_partial_tail_recovered(tmp_path:Path):
    p=tmp_path/"events.jsonl"; log=EventLog(p); log.append(type="a",payload={"x":1})
    with p.open("ab") as h: h.write(b'{"event_id":"partial"')
    log2=EventLog(p)
    assert log2.count==1

def test_snapshot_integrity(tmp_path:Path):
    s=SnapshotStore(tmp_path/"snap"); d=s.write(name="x",payload={"a":1})
    assert s.read(d)=={"a":1}
