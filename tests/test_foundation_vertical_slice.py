from pathlib import Path

import pytest

from core.identity import ContentHash, hash_bytes
from core.montage.flatten import flatten
from core.montage.model import MediaAsset, new_clip_layer, new_timeline
from core.montage.operations import split_layer
from core.montage.repository import MontageRepository
from core.montage.validation import validate_project_v2
from core.project import Project
from core.project.events import EventLog, EventLogCorrupt
from core.project.time import RationalTime, TimeRange


def test_vertical_slice_project_to_restore_and_tamper(tmp_path: Path):
    root = tmp_path / "project.mypro"
    project = Project.create(root)
    repo = MontageRepository(project.log)

    asset = MediaAsset(
        id="shot-001",
        name="shot.mov",
        content_hash=hash_bytes(b"shot"),
        kind="video",
        duration=RationalTime(20),
        width=1920,
        height=1080,
        fps_num=24,
        fps_den=1,
    )
    repo.add_asset(asset)

    timeline = new_timeline("Main", fps_num=24, fps_den=1)
    repo.create_timeline(timeline)
    track_id = timeline.video_tracks[0].id
    clip = new_clip_layer(
        asset_id=asset.id,
        timeline_range=TimeRange(RationalTime(0), RationalTime(10)),
    )
    repo.add_video_layer(timeline.id, track_id, clip)
    split_layer(
        repo,
        timeline_id=timeline.id,
        track_id=track_id,
        layer_id=clip.id,
        at=RationalTime(5),
    )

    validate_project_v2(repo.timelines, repo.media_pool)
    flat = flatten(repo.timelines, timeline.id)
    assert len(flat.video_layers) == 2

    digest = project.backup(label="vertical-slice")
    assert project.verify_backup(digest)

    restored = project.restore_backup(digest, target=tmp_path / "restored.mypro")
    assert restored.log.tip_hash == project.log.tip_hash
    assert restored.log.count == project.log.count

    snapshot = root / "snapshots" / f"{digest.hex}.json"
    original = snapshot.read_text(encoding="utf-8")
    snapshot.write_text(original.replace('"events":', '"events":', 1) + "\n", encoding="utf-8")
    assert not project.verify_backup(digest)


def test_event_log_rejects_non_tail_corruption(tmp_path: Path):
    path = tmp_path / "events.jsonl"
    log = EventLog(path)
    log.append(type="one", payload={"value": 1})
    log.append(type="two", payload={"value": 2})

    raw = path.read_bytes().splitlines(keepends=True)
    raw[0] = raw[0].replace(b'"value":1', b'"value":9')
    path.write_bytes(b"".join(raw))

    with pytest.raises(EventLogCorrupt):
        list(EventLog(path).iter_events())
