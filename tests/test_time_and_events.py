from fractions import Fraction

from core.project.events import EventLog, ProjectEvent
from core.project.time import RationalTime, TimeRange


def test_rational_time_is_exact():
    value = RationalTime(30000, 1001)
    assert value.fraction == Fraction(30000, 1001)


def test_time_range_is_half_open():
    interval = TimeRange(RationalTime(0), RationalTime(10))
    assert interval.contains(RationalTime(0))
    assert interval.contains(RationalTime(9))
    assert not interval.contains(RationalTime(10))


def test_event_log_is_append_only(tmp_path):
    path = tmp_path / "events.jsonl"
    log = EventLog(path)
    log.append(ProjectEvent("1", "project.created", {"name": "demo"}))
    log.append(ProjectEvent("2", "decision.recorded", {"approved": True}))

    events = log.read_all()
    assert [event["event_id"] for event in events] == ["1", "2"]
    assert path.read_text(encoding="utf-8").count("\n") == 2
