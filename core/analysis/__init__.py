"""Analysis primitives: observations, provenance, analyzer contracts and domain measurements."""

from .cinema_catharsis import (
    CatharsisEvent,
    category_coverage,
    category_duration,
    category_jaccard,
    category_union_duration,
    coding_uncertainty,
    event_count,
    event_density_per_minute,
    episode_repeatability,
    normalized_category_share,
    normalized_entropy,
    screen_time_share,
)

__all__ = [
    "CatharsisEvent",
    "category_coverage",
    "category_duration",
    "category_jaccard",
    "category_union_duration",
    "coding_uncertainty",
    "event_count",
    "event_density_per_minute",
    "episode_repeatability",
    "normalized_category_share",
    "normalized_entropy",
    "screen_time_share",
]
