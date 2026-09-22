from hypothesis import given, strategies as st
from core.project import EventLog, ProjectEvent


@given(st.lists(st.integers(min_value=0, max_value=1000), max_size=20))
def test_event_chain_survives_arbitrary_append_sequences(tmp_path, values):
    path = tmp_path / "events.jsonl"
    log = EventLog(path)
    for index, value in enumerate(values):
        log.append(ProjectEvent(str(index), "test", {"value": value}))
    recovered = EventLog(path)
    assert recovered.count == len(values)
    assert recovered.tip_hash == log.tip_hash
