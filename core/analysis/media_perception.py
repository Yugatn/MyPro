"""Typed records for stimulus exposure and task-specific perception outcomes.

These records describe observations and measured responses; exposure is not proof
of detection, recognition, memory, or a causal media effect.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Literal

from core.project.time import TimeRange

TaskType = Literal[
    "detection", "identification", "confidence", "free_recall", "recognition",
    "source_memory", "delayed_recall", "delayed_recognition",
    "physiological_measure", "attitude", "behavior",
]

@dataclass(frozen=True)
class StimulusExposure:
    """A source-media exposure annotation using exact rational intervals."""

    asset_id: str
    asset_hash: str
    timebase_id: str
    intervals: tuple[TimeRange, ...]
    annotation_method: str
    provenance_id: str

    def __post_init__(self) -> None:
        if not all((self.asset_id, self.asset_hash, self.timebase_id, self.annotation_method, self.provenance_id)):
            raise ValueError("asset, timebase, method and provenance fields are required")
        if not self.intervals:
            raise ValueError("at least one exposure interval is required")
        ordered = sorted(self.intervals, key=lambda item: item.start.fraction)
        if tuple(ordered) != self.intervals:
            raise ValueError("intervals must be sorted by start time")

    @property
    def total_visible_duration(self) -> Fraction:
        """Sum of annotated exposure durations; overlapping intervals are not merged."""
        return sum((interval.duration for interval in self.intervals), Fraction(0, 1))

    @property
    def longest_contiguous_duration(self) -> Fraction:
        return max((interval.duration for interval in self.intervals), default=Fraction(0, 1))

    @property
    def presentation_count(self) -> int:
        return len(self.intervals)

@dataclass(frozen=True)
class ParticipantOutcome:
    """One task-specific response; identity should be study-local and pseudonymous."""

    study_id: str
    trial_id: str
    participant_id: str
    task_type: TaskType
    response: str | bool | int | float | None
    protocol_version: str
    assessment_delay_seconds: Fraction | None = None
    correctness: bool | None = None
    reaction_time_seconds: Fraction | None = None

    def __post_init__(self) -> None:
        if not all((self.study_id, self.trial_id, self.participant_id, self.protocol_version)):
            raise ValueError("study, trial, pseudonymous participant and protocol are required")
        if self.assessment_delay_seconds is not None and self.assessment_delay_seconds < 0:
            raise ValueError("assessment delay cannot be negative")
        if self.reaction_time_seconds is not None and self.reaction_time_seconds < 0:
            raise ValueError("reaction time cannot be negative")
        if self.task_type in ("free_recall", "recognition", "source_memory", "delayed_recall", "delayed_recognition") and self.assessment_delay_seconds is None:
            raise ValueError("memory outcomes require an explicit assessment delay")

@dataclass(frozen=True)
class ThresholdEstimate:
    """A task- and population-specific threshold estimate, never a universal constant."""

    study_id: str
    task_type: TaskType
    criterion_description: str
    population_description: str
    estimate_seconds: Fraction
    lower_bound_seconds: Fraction
    upper_bound_seconds: Fraction
    model_version: str
    data_hash: str

    def __post_init__(self) -> None:
        if not all((self.study_id, self.criterion_description, self.population_description, self.model_version, self.data_hash)):
            raise ValueError("threshold provenance and criterion fields are required")
        if self.estimate_seconds < 0 or self.lower_bound_seconds < 0 or self.upper_bound_seconds < 0:
            raise ValueError("threshold values cannot be negative")
        if not self.lower_bound_seconds <= self.estimate_seconds <= self.upper_bound_seconds:
            raise ValueError("estimate must lie inside its uncertainty interval")

    def to_dict(self) -> dict[str, object]:
        return {
            "study_id": self.study_id,
            "task_type": self.task_type,
            "criterion_description": self.criterion_description,
            "population_description": self.population_description,
            "estimate_seconds": _fraction_dict(self.estimate_seconds),
            "uncertainty_interval_seconds": {
                "lower": _fraction_dict(self.lower_bound_seconds),
                "upper": _fraction_dict(self.upper_bound_seconds),
            },
            "model_version": self.model_version,
            "data_hash": self.data_hash,
        }

def _fraction_dict(value: Fraction) -> dict[str, int]:
    return {"num": value.numerator, "den": value.denominator}