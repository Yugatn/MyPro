"""Cinema Catharsis descriptive measurement primitives.

This module measures coded media. It does not estimate viewer harm,
viewer attitudes, or causal effects.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import log
from typing import Iterable

@dataclass(frozen=True)
class CatharsisEvent:
    category: str
    start: Fraction
    end: Fraction
    weight: Fraction = Fraction(1, 1)
    confidence: Fraction | None = None
    episode_id: str | None = None

    def __post_init__(self) -> None:
        if not self.category.strip():
            raise ValueError("category is required")
        if self.start < 0 or self.end <= self.start:
            raise ValueError("event must satisfy 0 <= start < end")
        if not 0 <= self.weight <= 1:
            raise ValueError("weight must be between 0 and 1")
        if self.confidence is not None and not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")

def _merge_duration(intervals: Iterable[tuple[Fraction, Fraction]]) -> Fraction:
    ordered = sorted(intervals)
    if not ordered:
        return Fraction(0)
    total = Fraction(0)
    current_start, current_end = ordered[0]
    for start, end in ordered[1:]:
        if start <= current_end:
            current_end = max(current_end, end)
        else:
            total += current_end - current_start
            current_start, current_end = start, end
    return total + current_end - current_start

def event_count(events: Iterable[CatharsisEvent], category: str) -> Fraction:
    return sum((e.weight for e in events if e.category == category), Fraction(0))

def category_duration(events: Iterable[CatharsisEvent], category: str) -> Fraction:
    return _merge_duration((e.start, e.end) for e in events if e.category == category)

def screen_time_share(events: Iterable[CatharsisEvent], category: str, total_duration: Fraction) -> Fraction:
    if total_duration <= 0:
        raise ValueError("total_duration must be positive")
    return category_duration(events, category) / total_duration

def event_density_per_minute(events: Iterable[CatharsisEvent], category: str, total_duration: Fraction) -> Fraction:
    if total_duration <= 0:
        raise ValueError("total_duration must be positive")
    return event_count(events, category) / (total_duration / 60)

def category_coverage(events: Iterable[CatharsisEvent], category: str, target_duration: Fraction) -> Fraction:
    if target_duration <= 0:
        raise ValueError("target_duration must be positive")
    return min(category_duration(events, category) / target_duration, Fraction(1))

def episode_repeatability(events: Iterable[CatharsisEvent], category: str, episode_ids: Iterable[str]) -> Fraction:
    episodes = set(episode_ids)
    if not episodes:
        raise ValueError("episode_ids must not be empty")
    observed = {e.episode_id for e in events if e.category == category and e.episode_id is not None}
    return Fraction(len(observed & episodes), len(episodes))

def normalized_category_share(events: Iterable[CatharsisEvent], category: str, categories: Iterable[str]) -> Fraction:
    shares = {c: category_duration(events, c) for c in categories}
    total = sum(shares.values(), Fraction(0))
    return Fraction(0) if total == 0 else shares.get(category, Fraction(0)) / total

def normalized_entropy(events: Iterable[CatharsisEvent], categories: Iterable[str]) -> float:
    cats = tuple(dict.fromkeys(categories))
    durations = [category_duration(events, c) for c in cats]
    total = sum(durations, Fraction(0))
    if total == 0 or len(cats) <= 1:
        return 0.0
    probabilities = [float(d / total) for d in durations if d]
    h = -sum(p * log(p) for p in probabilities)
    return h / log(len(cats))

def category_union_duration(events: Iterable[CatharsisEvent], categories: Iterable[str]) -> Fraction:
    selected = set(categories)
    return _merge_duration((e.start, e.end) for e in events if e.category in selected)

def coding_uncertainty(events: Iterable[CatharsisEvent], category: str) -> Fraction:
    values = [e.confidence for e in events if e.category == category and e.confidence is not None]
    if not values:
        return Fraction(1, 1)
    return 1 - sum(values, Fraction(0)) / len(values)

def category_jaccard(events: Iterable[CatharsisEvent], left: str, right: str) -> Fraction:
    left_intervals = [(e.start, e.end) for e in events if e.category == left]
    right_intervals = [(e.start, e.end) for e in events if e.category == right]
    points = sorted({p for interval in left_intervals + right_intervals for p in interval})
    intersection = Fraction(0)
    union = Fraction(0)
    for a, b in zip(points, points[1:]):
        if b <= a:
            continue
        in_left = any(s <= a and b <= e for s, e in left_intervals)
        in_right = any(s <= a and b <= e for s, e in right_intervals)
        if in_left and in_right:
            intersection += b - a
        if in_left or in_right:
            union += b - a
    return Fraction(0) if union == 0 else intersection / union