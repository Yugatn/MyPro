import pytest

from core.analysis.psychometric_fit import PsychometricBin, fit_logistic_mle
from core.analysis.psychometric import LogisticPsychometricModel

def test_fit_recovers_approximate_midpoint_from_synthetic_bins():
    source = LogisticPsychometricModel(0.2, 25.0)
    durations = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35]
    bins = tuple(PsychometricBin(t, round(source.probability(t) * 100), 100) for t in durations)
    fit = fit_logistic_mle(bins, max_iterations=1000)
    assert fit.converged
    assert fit.model.midpoint_seconds == pytest.approx(0.2, abs=0.04)
    assert fit.negative_log_likelihood >= 0

def test_fit_rejects_unidentifiable_constant_responses():
    bins = (PsychometricBin(0.1, 5, 10), PsychometricBin(0.2, 5, 10), PsychometricBin(0.3, 5, 10))
    with pytest.raises(ValueError, match="not identifiable"):
        fit_logistic_mle(bins)

def test_fit_requires_three_distinct_durations():
    bins = (PsychometricBin(0.1, 4, 10), PsychometricBin(0.1, 6, 10), PsychometricBin(0.1, 8, 10))
    with pytest.raises(ValueError, match="three distinct"):
        fit_logistic_mle(bins)

def test_fit_rejects_invalid_counts():
    with pytest.raises(ValueError):
        PsychometricBin(0.1, 11, 10)