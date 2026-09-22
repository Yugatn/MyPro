import pytest

from core.analysis.model import AnalyzerIdentity, Observation


def test_observation_preserves_uncertainty_and_status():
    obs = Observation(
        id="obs-1",
        type="scene_boundary",
        asset_id="asset-1",
        value=12.5,
        confidence=0.81,
        uncertainty=0.12,
        status="observed",
        provenance_id="prov-1",
        analyzer=AnalyzerIdentity("scene", "0.1.0", "code", "config"),
    )

    data = obs.to_dict()
    assert data["uncertainty"] == 0.12
    assert data["status"] == "observed"
    assert data["analyzer"]["version"] == "0.1.0"


def test_observation_rejects_invalid_confidence():
    with pytest.raises(ValueError):
        Observation(
            id="obs-1",
            type="x",
            asset_id="asset-1",
            value=True,
            confidence=1.1,
            uncertainty=None,
            status="unknown",
        )
