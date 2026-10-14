"""Binomial maximum-likelihood fitting for aggregate psychometric trials.

This is a lightweight research prototype. It does not handle participant-level
random effects and should not be used to claim population-general thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite, log
from typing import Iterable

from core.analysis.psychometric import LogisticPsychometricModel

@dataclass(frozen=True)
class PsychometricBin:
    duration_seconds: float
    correct: int
    total: int

    def __post_init__(self) -> None:
        if not isfinite(self.duration_seconds) or self.duration_seconds < 0:
            raise ValueError("duration must be finite and non-negative")
        if self.total <= 0 or self.correct < 0 or self.correct > self.total:
            raise ValueError("counts must satisfy total > 0 and 0 <= correct <= total")

@dataclass(frozen=True)
class FitResult:
    model: LogisticPsychometricModel
    negative_log_likelihood: float
    converged: bool
    iterations: int
    message: str
    bins_used: int
    trials_used: int

def _nll(midpoint: float, log_slope: float, bins: tuple[PsychometricBin, ...], guess: float, lapse: float) -> float:
    slope = exp(log_slope)
    model = LogisticPsychometricModel(midpoint, slope, guess, lapse)
    total = 0.0
    for item in bins:
        p = min(1.0 - 1e-12, max(1e-12, model.probability(item.duration_seconds)))
        total -= item.correct * log(p) + (item.total - item.correct) * log(1.0 - p)
    return total

def fit_logistic_mle(
    observations: Iterable[PsychometricBin],
    *,
    guess_rate: float = 0.0,
    lapse_rate: float = 0.0,
    max_iterations: int = 500,
    tolerance: float = 1e-8,
) -> FitResult:
    """Fit midpoint and positive slope by deterministic coordinate search.

    Guess and lapse rates are fixed by caller, not estimated. The returned fit
    has no confidence interval; report it as a prototype point estimate only.
    """
    bins = tuple(observations)
    if len(bins) < 3:
        raise ValueError("at least three duration bins are required")
    if len({b.duration_seconds for b in bins}) < 3:
        raise ValueError("at least three distinct durations are required")
    if max_iterations <= 0 or tolerance <= 0:
        raise ValueError("max_iterations and tolerance must be positive")
    # Reject unidentifiable boundary patterns instead of returning a misleading fit.
    rates = [b.correct / b.total for b in bins]
    if max(rates) - min(rates) < 1e-12:
        raise ValueError("responses do not vary across bins; fit is not identifiable")
    if not 0 <= guess_rate < 1 or not 0 <= lapse_rate < 1 or guess_rate + lapse_rate >= 1:
        raise ValueError("invalid guess/lapse rates")
    low_t = min(b.duration_seconds for b in bins)
    high_t = max(b.duration_seconds for b in bins)
    span = max(high_t - low_t, 1e-6)
    midpoint = (low_t + high_t) / 2
    log_slope = log(4.0 / span)
    best = _nll(midpoint, log_slope, bins, guess_rate, lapse_rate)
    step_mid = span / 2
    step_slope = 1.0
    converged = False
    message = "iteration limit reached"
    for iteration in range(1, max_iterations + 1):
        improved = False
        candidates = (
            (midpoint - step_mid, log_slope), (midpoint + step_mid, log_slope),
            (midpoint, log_slope - step_slope), (midpoint, log_slope + step_slope),
        )
        for candidate_mid, candidate_log_slope in candidates:
            candidate_mid = max(0.0, candidate_mid)
            candidate_log_slope = min(log(1e6 / span), max(log(1e-6 / span), candidate_log_slope))
            value = _nll(candidate_mid, candidate_log_slope, bins, guess_rate, lapse_rate)
            if value + tolerance < best:
                midpoint, log_slope, best = candidate_mid, candidate_log_slope, value
                improved = True
        if not improved:
            step_mid *= 0.5
            step_slope *= 0.5
        if step_mid < tolerance and step_slope < tolerance:
            converged = True
            message = "coordinate search step tolerance reached"
            break
    return FitResult(
        model=LogisticPsychometricModel(midpoint, exp(log_slope), guess_rate, lapse_rate),
        negative_log_likelihood=best, converged=converged, iterations=iteration,
        message=message, bins_used=len(bins), trials_used=sum(b.total for b in bins),
    )