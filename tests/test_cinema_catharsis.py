from fractions import Fraction

from core.analysis.cinema_catharsis import (
    CatharsisEvent, category_coverage, category_duration, category_jaccard,
    category_union_duration, coding_uncertainty, event_count,
    event_density_per_minute, episode_repeatability, normalized_entropy,
    normalized_category_share, screen_time_share,
)

def f(value: int) -> Fraction:
    return Fraction(value, 1)

def test_descriptive_metrics_use_exact_time_and_union_overlap():
    events = [
        CatharsisEvent("consumption", f(0), f(30), confidence=f(1)),
        CatharsisEvent("consumption", f(20), f(50), confidence=f(3) / 4),
        CatharsisEvent("communication", f(40), f(70)),
    ]
    assert event_count(events, "consumption") == f(2)
    assert category_duration(events, "consumption") == f(50)
    assert screen_time_share(events, "consumption", f(100)) == f(1) / 2
    assert event_density_per_minute(events, "consumption", f(120)) == f(1)
    assert category_union_duration(events, {"consumption", "communication"}) == f(70)

def test_coverage_repeatability_entropy_and_uncertainty():
    events = [
        CatharsisEvent("action", f(0), f(10), confidence=f(9) / 10, episode_id="a"),
        CatharsisEvent("action", f(20), f(30), confidence=f(7) / 10, episode_id="b"),
        CatharsisEvent("care", f(40), f(60), episode_id="a"),
    ]
    assert category_coverage(events, "action", f(20)) == f(1)
    assert episode_repeatability(events, "action", ["a", "b", "c"]) == f(2) / 3
    assert normalized_category_share(events, "action", ["action", "care"]) == f(1) / 2
    assert 0.0 <= normalized_entropy(events, ["action", "care"]) <= 1.0
    assert coding_uncertainty(events, "action") == f(1) / 5

def test_jaccard_is_duration_based():
    events = [CatharsisEvent("a", f(0), f(10)), CatharsisEvent("b", f(5), f(15))]
    assert category_jaccard(events, "a", "b") == f(1) / 3