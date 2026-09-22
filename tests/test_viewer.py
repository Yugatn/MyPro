from fractions import Fraction

from core.project.time import RationalTime, TimeRange
from core.viewer import ViewerAction, ViewerMode, ViewerSelection
from core.viewer.model import ViewerIntent


def test_viewer_selection_preserves_exact_time_and_publication() -> None:
    selection = ViewerSelection(
        content_id="video-1",
        published_version_id="pub-7",
        time_range=TimeRange(
            RationalTime.from_seconds(Fraction(25, 24)),
            RationalTime.from_seconds(Fraction(37, 24)),
        ),
    )
    assert selection.start.fraction == Fraction(25, 24)
    assert selection.end.fraction == Fraction(37, 24)
    assert selection.published_version_id == "pub-7"


def test_viewer_intent_is_explicit() -> None:
    selection = ViewerSelection(
        "video-1",
        None,
        TimeRange(RationalTime(0), RationalTime(1)),
    )
    intent = ViewerIntent(
        ViewerAction.ADD_TO_MONTAGE,
        selection,
        "request-1",
        "user-1",
    )
    assert ViewerMode.WATCH.value == "watch"
    assert intent.action is ViewerAction.ADD_TO_MONTAGE
    assert intent.selection.content_id == "video-1"
