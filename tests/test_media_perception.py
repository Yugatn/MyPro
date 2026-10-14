from fractions import Fraction

import pytest

from core.analysis.media_perception import ParticipantOutcome, StimulusExposure, ThresholdEstimate
from core.project.time import RationalTime, TimeRange

def test_exposure_durations_use_exact_rational_time():
    exposure = StimulusExposure(
        asset_id="asset-1", asset_hash="sha256:abc", timebase_id="fps-30000-1001",
        intervals=(
            TimeRange(RationalTime(0), RationalTime(1, 10)),
            TimeRange(RationalTime(1), RationalTime(11, 10)),
        ), annotation_method="manual", provenance_id="prov-1",
    )
    assert exposure.total_visible_duration == Fraction(1, 5)
    assert exposure.longest_contiguous_duration == Fraction(1, 10)
    assert exposure.presentation_count == 2

def test_exposure_requires_sorted_nonempty_intervals():
    with pytest.raises(ValueError):
        StimulusExposure(
            asset_id="a", asset_hash="h", timebase_id="tb",
            intervals=(TimeRange(RationalTime(2), RationalTime(3)), TimeRange(RationalTime(0), RationalTime(1))),
            annotation_method="manual", provenance_id="p",
        )

def test_memory_outcome_requires_assessment_delay():
    with pytest.raises(ValueError):
        ParticipantOutcome("study", "trial", "pseudonym-1", "recognition", True, "v1")

def test_threshold_estimate_requires_valid_interval():
    with pytest.raises(ValueError):
        ThresholdEstimate("s", "detection", "75% correct", "sample A", Fraction(1, 10), Fraction(1, 5), Fraction(3, 10), "m1", "hash")

def test_threshold_serializes_exact_fractions():
    estimate = ThresholdEstimate("s", "detection", "75% correct", "sample A", Fraction(1, 10), Fraction(1, 20), Fraction(1, 5), "m1", "sha256:data")
    data = estimate.to_dict()
    assert data["estimate_seconds"] == {"num": 1, "den": 10}
    assert data["uncertainty_interval_seconds"]["lower"] == {"num": 1, "den": 20}