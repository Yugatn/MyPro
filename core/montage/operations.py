"""Transactional montage operations implemented as event-backed state changes."""
from __future__ import annotations
from core.project.time import RationalTime, TimeRange
from .model import LayerKind, Timeline, VideoLayer, new_compound_layer
from .repository import MontageRepository


def _replace_track(repo, timeline_id, track_id, layers):
    tl=repo.timelines[timeline_id]
    tracks=tuple(t.with_layers(tuple(layers)) if t.id==track_id else t for t in tl.video_tracks)
    repo._set(tl.with_video_tracks(tracks))


def split_layer(repo: MontageRepository, *, timeline_id: str, track_id: str, layer_id: str, at: RationalTime):
    tl=repo.timelines[timeline_id]; track=next(t for t in tl.video_tracks if t.id==track_id)
    layer=next(l for l in track.layers if l.id==layer_id)
    if not layer.range.contains(at):
        raise ValueError("split point must be inside layer")
    left=layer.with_range(TimeRange(layer.range.start,at))
    right=layer.with_range(TimeRange(at,layer.range.end))
    layers=tuple(x for x in track.layers if x.id!=layer_id)
    pos=next(i for i,x in enumerate(track.layers) if x.id==layer_id)
    _replace_track(repo,timeline_id,track_id,layers[:pos]+(left,right)+layers[pos:])
    return left,right


def move_layer(repo, *, timeline_id, from_track_id, layer_id, to_track_id, at=None):
    tl=repo.timelines[timeline_id]
    src=next(t for t in tl.video_tracks if t.id==from_track_id)
    layer=next(l for l in src.layers if l.id==layer_id)
    start=at or layer.range.start
    duration=layer.range.duration
    moved=layer.with_range(TimeRange(start,start+duration))
    src_layers=tuple(x for x in src.layers if x.id!=layer_id)
    dst=next(t for t in tl.video_tracks if t.id==to_track_id)
    dst_layers=dst.layers+(moved,)
    tracks=tuple((t.with_layers(src_layers) if t.id==src.id else t.with_layers(dst_layers) if t.id==dst.id else t) for t in tl.video_tracks)
    repo._set(tl.with_video_tracks(tracks))
    return moved


def trim_layer(repo, *, timeline_id, track_id, layer_id, new_range, mode="overwrite"):
    if mode not in {"overwrite","ripple"}:
        raise ValueError("unsupported trim mode")
    tl=repo.timelines[timeline_id]; track=next(t for t in tl.video_tracks if t.id==track_id)
    old=next(l for l in track.layers if l.id==layer_id)
    delta=new_range.end.fraction-old.range.end.fraction
    layers=[]
    for l in track.layers:
        if l.id==layer_id:
            layers.append(l.with_range(new_range))
        elif mode=="ripple" and l.range.start.fraction>=old.range.end.fraction:
            from fractions import Fraction
            s=l.range.start.fraction+delta; e=l.range.end.fraction+delta
            layers.append(l.with_range(TimeRange(RationalTime.from_seconds(s),RationalTime.from_seconds(e))))
        else:
            layers.append(l)
    _replace_track(repo,timeline_id,track_id,layers)
    return next(l for l in layers if l.id==layer_id)


def create_compound(repo, *, source_timeline_id, layer_ids, name):
    source=repo.timelines[source_timeline_id]; selected=[]
    for track in source.video_tracks:
        selected.extend([l for l in track.layers if l.id in set(layer_ids)])
    if not selected:
        raise ValueError("no layers selected")
    start=min(l.range.start.fraction for l in selected); end=max(l.range.end.fraction for l in selected)
    nested_id=f"tl_compound_{__import__('uuid').uuid4().hex}"
    nested=Timeline(nested_id,f"{name}:nested",source.fps_num,source.fps_den,source.video_tracks,source.audio_tracks,source_timeline_id,source.audio_sample_rate)
    repo.create_timeline(nested)
    compound=new_compound_layer(timeline_id=nested_id,timeline_range=TimeRange(RationalTime.from_seconds(start),RationalTime.from_seconds(end)),name=name)
    track=source.video_tracks[0]
    remaining=tuple(l for l in track.layers if l.id not in set(layer_ids))
    _replace_track(repo,source_timeline_id,track.id,remaining+(compound,))
    return nested_id,compound
