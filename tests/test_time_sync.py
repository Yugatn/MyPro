from core.project.time import ClockRef, RationalTime, SyncGroup, SyncPoint


def test_sync_group_is_explicit():
    clock = ClockRef("ptp", "epoch-1", RationalTime(48000, 1))
    point = SyncPoint(clock, RationalTime(100, 25), RationalTime(2000, 1))
    group = SyncGroup("cam-group", ("cam-a", "cam-b"), (point,), clock)
    assert group.external_clock == clock
