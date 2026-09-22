"""End-to-end Foundation v0.4 demo."""
from __future__ import annotations
import sys
from pathlib import Path
from core.identity import hash_bytes
from core.project import Project
from core.project.time import RationalTime, TimeRange
from core.montage.model import MediaAsset,new_clip_layer,new_timeline
from core.montage.repository import MontageRepository
from core.montage.operations import split_layer,create_compound
from core.montage.flatten import flatten
from core.montage.validation import validate_project_v2


def main(work: Path):
    work.mkdir(parents=True,exist_ok=True)
    project=Project.create(work/"demo.mypro")
    repo=MontageRepository(project.log)
    repo.add_asset(MediaAsset("asset_a","interview.mov",hash_bytes(b"fake_video_a"),"video",RationalTime(60),1920,1080,24,1))
    repo.add_asset(MediaAsset("asset_b","broll.mov",hash_bytes(b"fake_video_b"),"video",RationalTime(45),1920,1080,24,1))
    tl=new_timeline("Main")
    repo.create_timeline(tl)
    v1=tl.video_tracks[0].id
    a=new_clip_layer(asset_id="asset_a",timeline_range=TimeRange(RationalTime(0),RationalTime(20)),name="interview")
    b=new_clip_layer(asset_id="asset_b",timeline_range=TimeRange(RationalTime(20),RationalTime(35)),name="broll")
    repo.add_video_layer(tl.id,v1,a); repo.add_video_layer(tl.id,v1,b)
    left,right=split_layer(repo,timeline_id=tl.id,track_id=v1,layer_id=a.id,at=RationalTime(8))
    nested,compound=create_compound(repo,source_timeline_id=tl.id,layer_ids=[left.id,right.id],name="interview_block")
    flat=flatten(repo.timelines,tl.id)
    validate_project_v2(repo.timelines,repo.media_pool)
    digest=project.backup(label="demo")
    assert project.verify_backup(digest)
    restored=project.restore_backup(digest,target=work/"restored.mypro")
    assert restored.log.tip_hash==project.log.tip_hash
    print(f"timeline={tl.id} compound={nested} flat_video_layers={len(flat.video_layers)}")
    print(f"backup={digest} events={project.log.count}")
    print("All Foundation v0.4 checks passed.")


if __name__=="__main__":
    main(Path(sys.argv[1] if len(sys.argv)>1 else "/tmp/mypro-demo"))
