"""Resolve compound timelines into renderer-friendly flat layers."""
from __future__ import annotations
from dataclasses import dataclass
from core.project.time import RationalTime, TimeRange
from .model import Timeline, VideoLayer, LayerKind


@dataclass(frozen=True)
class FlatLayer:
    path: tuple[str,...]
    track_index: int
    layer: VideoLayer
    effective_range: TimeRange


@dataclass(frozen=True)
class FlatTimeline:
    duration: RationalTime
    video_layers: tuple[FlatLayer,...]
    audio_layers: tuple[FlatLayer,...]


def flatten(timelines: dict[str,Timeline], timeline_id: str) -> FlatTimeline:
    out=[]
    visiting=set()
    def walk(tid, parent_start=None, path=()):
        if parent_start is None:
            parent_start = RationalTime(0, 1)
        if tid in visiting:
            raise ValueError("timeline cycle")
        visiting.add(tid)
        tl=timelines[tid]
        for track in tl.video_tracks:
            for layer in track.layers:
                start=parent_start+layer.range.start
                end=parent_start+layer.range.end
                if layer.kind is LayerKind.COMPOUND:
                    walk(layer.nested_timeline_id,start,path+(tid,))
                else:
                    out.append(FlatLayer(path+(tid,),track.index,layer,TimeRange(start,end)))
        visiting.remove(tid)
    walk(timeline_id)
    return FlatTimeline(timelines[timeline_id].duration,tuple(out),())
