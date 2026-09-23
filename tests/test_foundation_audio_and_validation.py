from pathlib import Path
import pytest

from core.identity import hash_bytes
from core.montage.flatten import flatten
from core.montage.model import AudioLayer, MediaAsset, new_timeline
from core.montage.repository import MontageRepository
from core.montage.validation import InvariantViolation, validate_project_v2
from core.project.events import EventLog
from core.project.time import RationalTime, TimeRange


def test_audio_layer_survives_event_replay(tmp_path: Path):
    log = EventLog(tmp_path / "events.jsonl")
    repo = MontageRepository(log)
    repo.add_asset(MediaAsset("a", "audio.wav", hash_bytes(b"a"), "audio", RationalTime(20)))
    timeline = new_timeline("Main")
    repo.create_timeline(timeline)
    layer = AudioLayer("al", "music", TimeRange(RationalTime(2), RationalTime(8)), "a")
    tl = repo.timelines[timeline.id]
    track = tl.audio_tracks[0]
    repo._set(tl.with_audio_tracks(tuple(
        t.with_layers((layer,)) if t.id == track.id else t for t in tl.audio_tracks
    )))

    replayed = MontageRepository(EventLog(tmp_path / "events.jsonl"))
    assert replayed.timelines[timeline.id].audio_tracks[0].layers == (layer,)


def test_flatten_includes_audio_and_effective_duration(tmp_path: Path):
    log = EventLog(tmp_path / "events.jsonl")
    repo = MontageRepository(log)
    repo.add_asset(MediaAsset("a", "audio.wav", hash_bytes(b"a"), "audio", RationalTime(20)))
    timeline = new_timeline("Main")
    repo.create_timeline(timeline)
    layer = AudioLayer("al", "music", TimeRange(RationalTime(3), RationalTime(11)), "a")
    tl = repo.timelines[timeline.id]
    repo._set(tl.with_audio_tracks(tuple(
        t.with_layers((layer,)) if t.id == tl.audio_tracks[0].id else t for t in tl.audio_tracks
    )))
    flat = flatten(repo.timelines, timeline.id)
    assert len(flat.audio_layers) == 1
    assert flat.duration == RationalTime(11)


def test_validation_rejects_disconnected_cycle():
    a = new_timeline("A")
    b = new_timeline("B", parent_timeline_id=a.id)
    a = a.with_video_tracks(a.video_tracks)
    b = b.with_video_tracks(b.video_tracks)
    from core.montage.model import VideoLayer, LayerKind
    cycle_a = VideoLayer("ca", LayerKind.COMPOUND, "B", TimeRange(RationalTime(0), RationalTime(1)), nested_timeline_id=b.id)
    cycle_b = VideoLayer("cb", LayerKind.COMPOUND, "A", TimeRange(RationalTime(0), RationalTime(1)), nested_timeline_id=a.id)
    a = a.with_video_tracks((a.video_tracks[0].with_layers((cycle_a,)), *a.video_tracks[1:]))
    b = b.with_video_tracks((b.video_tracks[0].with_layers((cycle_b,)), *b.video_tracks[1:]))
    with pytest.raises(InvariantViolation, match="I_timeline_no_cycle"):
        validate_project_v2({a.id: a, b.id: b}, {})
