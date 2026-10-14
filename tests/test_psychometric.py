import pytest

from core.analysis.psychometric import LogisticPsychometricModel, empirical_accuracy

def test_logistic_midpoint_is_between_asymptotes():
    model = LogisticPsychometricModel(0.2, 20.0, guess_rate=0.25, lapse_rate=0.02)
    assert model.probability(0.2) == pytest.approx(0.615)

def test_logistic_inverse_round_trips_probability():
    model = LogisticPsychometricModel(0.15, 12.0, guess_rate=0.0, lapse_rate=0.01)
    duration = model.duration_at_probability(0.75)
    assert model.probability(duration) == pytest.approx(0.75)

def test_threshold_rejects_unreachable_probability():
    model = LogisticPsychometricModel(0.1, 8.0, guess_rate=0.2, lapse_rate=0.05)
    with pytest.raises(ValueError):
        model.duration_at_probability(0.95)

def test_empirical_accuracy_validates_counts():
    assert empirical_accuracy(7, 10) == pytest.approx(0.7)
    with pytest.raises(ValueError):
        empirical_accuracy(11, 10)