"""Small dependency-free psychometric utilities for research prototypes.

These functions evaluate a declared logistic response model. They do not fit
participant data, estimate uncertainty, or establish a universal perception threshold.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite, log

@dataclass(frozen=True)
class LogisticPsychometricModel:
    """Logistic probability model for a binary task response.

    midpoint_seconds is the 50% point between guess and upper asymptote, not
    necessarily 50% raw accuracy when guess_rate is nonzero.
    """

    midpoint_seconds: float
    slope_per_second: float
    guess_rate: float = 0.0
    lapse_rate: float = 0.0

    def __post_init__(self) -> None:
        if not isfinite(self.midpoint_seconds) or self.midpoint_seconds < 0:
            raise ValueError("midpoint_seconds must be finite and non-negative")
        if not isfinite(self.slope_per_second) or self.slope_per_second <= 0:
            raise ValueError("slope_per_second must be finite and positive")
        if not 0 <= self.guess_rate < 1:
            raise ValueError("guess_rate must be in [0, 1)")
        if not 0 <= self.lapse_rate < 1:
            raise ValueError("lapse_rate must be in [0, 1)")
        if self.guess_rate + self.lapse_rate >= 1:
            raise ValueError("guess_rate + lapse_rate must be below 1")

    def probability(self, duration_seconds: float) -> float:
        """Return predicted response probability for a non-negative duration."""
        if not isfinite(duration_seconds) or duration_seconds < 0:
            raise ValueError("duration_seconds must be finite and non-negative")
        z = self.slope_per_second * (duration_seconds - self.midpoint_seconds)
        if z >= 0:
            logistic = 1.0 / (1.0 + exp(-z))
        else:
            exp_z = exp(z)
            logistic = exp_z / (1.0 + exp_z)
        return self.guess_rate + (1.0 - self.guess_rate - self.lapse_rate) * logistic

    def duration_at_probability(self, target_probability: float) -> float:
        """Invert the curve for a target within its asymptotic probability range."""
        if not isfinite(target_probability):
            raise ValueError("target_probability must be finite")
        lower = self.guess_rate
        upper = 1.0 - self.lapse_rate
        if not lower < target_probability < upper:
            raise ValueError("target probability must lie strictly between asymptotes")
        scaled = (target_probability - self.guess_rate) / (upper - lower)
        return self.midpoint_seconds + log(scaled / (1.0 - scaled)) / self.slope_per_second

def empirical_accuracy(correct: int, total: int) -> float:
    """Observed proportion correct; callers must preserve trial-level provenance."""
    if total <= 0:
        raise ValueError("total must be positive")
    if correct < 0 or correct > total:
        raise ValueError("correct must be between 0 and total")
    return correct / total