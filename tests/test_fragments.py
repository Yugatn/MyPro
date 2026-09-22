from fractions import Fraction
import pytest
from core.fragment import ContentFragment, FragmentIndex, FragmentKind, FragmentProposal, FragmentStatus
from core.project.time import RationalTime, TimeRange

def tr(start: int, end: int) -> TimeRange:
    return TimeRange(RationalTime.from_seconds(Fraction(start, 24)), RationalTime.from_seconds(Fraction(end, 24)))

def test_fragment_preserves_exact_source_and_time() -> None:
    fragment = ContentFragment("f1", "video-1", "sha256:abc", tr(24, 48), FragmentKind.SCENE, confidence=0.9, uncertainty=0.1)
    assert fragment.time_range.start.fraction == Fraction(1)
    assert fragment.time_range.end.fraction == Fraction(2)
    assert fragment.source_hash == "sha256:abc"

def test_index_queries() -> None:
    idx = FragmentIndex()
    idx.add(ContentFragment("a", "v1", "h1", tr(0, 24), FragmentKind.SCENE, label="opening"))
    idx.add(ContentFragment("b", "v1", "h1", tr(24, 48), FragmentKind.SPEECH, label="Hello world"))
    idx.add(ContentFragment("c", "v2", "h2", tr(12, 36), FragmentKind.ACTION, label="open door"))
    assert [x.id for x in idx.by_kind(FragmentKind.SPEECH)] == ["b"]
    assert [x.id for x in idx.by_source("v1")] == ["a", "b"]
    assert [x.id for x in idx.overlapping(tr(18, 30), source_content_id="v1")] == ["a", "b"]
    assert [x.id for x in idx.by_label("HELLO")] == ["b"]

def test_invalid_fragment_data_is_rejected() -> None:
    with pytest.raises(ValueError):
        ContentFragment("x", "v", "h", tr(0, 1), FragmentKind.SCENE, confidence=1.1)
    with pytest.raises(ValueError):
        ContentFragment("x", "v", "h", tr(0, 1), FragmentKind.COMPOSITE)

def test_proposal_is_not_an_action() -> None:
    fragment = ContentFragment("x", "v", "h", tr(0, 1), FragmentKind.SCENE)
    proposal = FragmentProposal("p1", (fragment.id,), "create clip", "analyzer:scene")
    assert proposal.fragment_ids == ("x",)
    assert fragment.status is FragmentStatus.CANDIDATE
