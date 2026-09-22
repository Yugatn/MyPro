from core.project.events import EventLog
from core.project.time import RationalTime,TimeRange
from core.montage.model import MediaAsset,new_clip_layer,new_timeline
from core.montage.repository import MontageRepository
from core.montage.operations import split_layer,create_compound
from core.montage.flatten import flatten
from core.montage.validation import validate_project_v2
from core.identity import hash_bytes

def test_end_to_end(tmp_path):
    repo=MontageRepository(EventLog(tmp_path/"events.jsonl"))
    repo.add_asset(MediaAsset("a","a.mov",hash_bytes(b"a"),"video",RationalTime(20)))
    tl=new_timeline("Main"); repo.create_timeline(tl); track=tl.video_tracks[0].id
    layer=new_clip_layer(asset_id="a",timeline_range=TimeRange(RationalTime(0),RationalTime(10)))
    repo.add_video_layer(tl.id,track,layer)
    left,right=split_layer(repo,timeline_id=tl.id,track_id=track,layer_id=layer.id,at=RationalTime(5))
    nested,_=create_compound(repo,source_timeline_id=tl.id,layer_ids=[left.id,right.id],name="C")
    flat=flatten(repo.timelines,tl.id)
    validate_project_v2(repo.timelines,repo.media_pool)
    assert nested in repo.timelines and len(flat.video_layers)==2
