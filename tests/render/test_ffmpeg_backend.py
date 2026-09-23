from core.identity import hash_bytes
from core.montage.model import MediaAsset, new_clip_layer, new_timeline
from core.montage.repository import MontageRepository
from core.project.events import EventLog
from core.project.time import RationalTime, TimeRange
from core.render.specification import RenderSpecification
from integrations.ffmpeg import FFmpegRenderer

def test_renderer_can_build_without_ffmpeg_execution(tmp_path):
    repo = MontageRepository(EventLog(tmp_path / "events.jsonl"))
    repo.add_asset(MediaAsset("a", "input.mov", hash_bytes(b"a"), "video", RationalTime(10)))
    timeline = new_timeline("Main")
    repo.create_timeline(timeline)
    repo.add_video_layer(timeline.id, timeline.video_tracks[0].id,
        new_clip_layer(asset_id="a", timeline_range=TimeRange(RationalTime(0), RationalTime(5))))
    result = FFmpegRenderer("ffmpeg").render(
        repo, RenderSpecification(timeline.id, str(tmp_path / "out.mp4")), execute=False)
    assert not result.executed
    assert result.return_code is None
    assert result.command[0] == "ffmpeg"
