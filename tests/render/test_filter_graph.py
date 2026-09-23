from core.identity import hash_bytes
from core.montage.flatten import flatten
from core.montage.model import MediaAsset, new_clip_layer, new_timeline
from core.montage.repository import MontageRepository
from core.project.events import EventLog
from core.project.time import RationalTime, TimeRange
from core.render.specification import RenderSpecification
from integrations.ffmpeg.filter_graph import build_ffmpeg_command

def test_ffmpeg_command_is_deterministic(tmp_path):
    repo = MontageRepository(EventLog(tmp_path / "events.jsonl"))
    repo.add_asset(MediaAsset("a", "input.mov", hash_bytes(b"a"), "video", RationalTime(10)))
    timeline = new_timeline("Main")
    repo.create_timeline(timeline)
    repo.add_video_layer(timeline.id, timeline.video_tracks[0].id,
        new_clip_layer(asset_id="a", timeline_range=TimeRange(RationalTime(0), RationalTime(5))))
    flat = flatten(repo.timelines, timeline.id)
    spec = RenderSpecification(timeline.id, "out.mp4")
    assert build_ffmpeg_command(flat, spec, {"a": "input.mov"}) == build_ffmpeg_command(flat, spec, {"a": "input.mov"})
