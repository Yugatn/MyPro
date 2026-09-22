"""Transactional montage operations implemented as event-backed state changes."""
from __future__ import annotations

from uuid import uuid4

from core.project.time import RationalTime, TimeRange
from .model import Timeline, VideoLayer, new_compound_layer
from .repository import MontageRepository


def _replace_track(repo, timeline_id, track_id, layers):
    tl = repo.timelines[timeline_id]
    tracks = tuple(
        t.with_layers(tuple(layers)) if t.id == track_id else t
        for t in tl.video_tracks
    )
    repo._set(tl.with_video_tracks(tracks))


def _new_layer_id(prefix: str = "vl") -> str:
    return f"{prefix}_{uuid4().hex}"


def split_layer(
    repo: MontageRepository,
    *,
    timeline_id: str,
    track_id: str,
    layer_id: str,
    at: RationalTime,
):
    tl = repo.timelines[timeline_id]
    track = next(t for t in tl.video_tracks if t.id == track_id)
    layer = next(l for l in track.layers if l.id == layer_id)
    if not layer.range.contains(at):
        raise ValueError("split point must be inside layer")

    left = layer.with_range(TimeRange(layer.range.start, at))
    right = layer.with_range(TimeRange(at, layer.range.end))
    left = VideoLayer(_new_layer_id(), left.kind, left.name, left.range,
                      left.source_id, left.nested_timeline_id)
    right = VideoLayer(_new_layer_id(), right.kind, right.name, right.range,
                       right.source_id, right.nested_timeline_id)

    pos = next(i for i, x in enumerate(track.layers) if x.id == layer_id)
    layers = tuple(x for x in track.layers if x.id != layer_id)
    _replace_track(repo, timeline_id, track_id, layers[:pos] + (left, right) + layers[pos:])
    return left, right


def move_layer(repo, *, timeline_id, from_track_id, layer_id, to_track_id, at=None):
    tl = repo.timelines[timeline_id]
    src = next(t for t in tl.video_tracks if t.id == from_track_id)
    dst = next(t for t in tl.video_tracks if t.id == to_track_id)
    layer = next(l for l in src.layers if l.id == layer_id)
    start = layer.range.start if at is None else at
    duration = layer.range.duration
    moved = layer.with_range(TimeRange(start, start + duration))

    if src.id == dst.id:
        layers = tuple(moved if x.id == layer_id else x for x in src.layers)
        _replace_track(repo, timeline_id, src.id, layers)
        return moved

    src_layers = tuple(x for x in src.layers if x.id != layer_id)
    dst_layers = dst.layers + (moved,)
    tracks = tuple(
        t.with_layers(src_layers) if t.id == src.id
        else t.with_layers(dst_layers) if t.id == dst.id
        else t
        for t in tl.video_tracks
    )
    repo._set(tl.with_video_tracks(tracks))
    return moved


def trim_layer(repo, *, timeline_id, track_id, layer_id, new_range, mode="overwrite"):
    if mode not in {"overwrite", "ripple"}:
        raise ValueError("unsupported trim mode")
    if new_range.end.fraction <= new_range.start.fraction:
        raise ValueError("new range must be positive")

    tl = repo.timelines[timeline_id]
    track = next(t for t in tl.video_tracks if t.id == track_id)
    old = next(l for l in track.layers if l.id == layer_id)

    delta = new_range.end.fraction - old.range.end.fraction
    layers = []
    for layer in track.layers:
        if layer.id == layer_id:
            layers.append(layer.with_range(new_range))
        elif mode == "ripple" and layer.range.start.fraction >= old.range.end.fraction:
            s = layer.range.start.fraction + delta
            e = layer.range.end.fraction + delta
            layers.append(
                layer.with_range(
                    TimeRange(RationalTime.from_seconds(s), RationalTime.from_seconds(e))
                )
            )
        else:
            layers.append(layer)

    _replace_track(repo, timeline_id, track_id, layers)
    return next(l for l in layers if l.id == layer_id)


def create_compound(repo, *, source_timeline_id, layer_ids, name):
    source = repo.timelines[source_timeline_id]
    selected_ids = set(layer_ids)
    if not selected_ids:
        raise ValueError("no layers selected")

    selected_by_track = {}
    selected = []
    for track in source.video_tracks:
        track_selected = [l for l in track.layers if l.id in selected_ids]
        if track_selected:
            selected_by_track[track.id] = track_selected
            selected.extend(track_selected)

    if not selected:
        raise ValueError("no layers selected")

    start = min(l.range.start.fraction for l in selected)
    end = max(l.range.end.fraction for l in selected)
    nested_id = f"tl_compound_{uuid4().hex}"

    nested_tracks = tuple(
        track.with_layers(tuple(selected_by_track.get(track.id, ())))
        for track in source.video_tracks
    )
    nested = Timeline(
        nested_id,
        f"{name}:nested",
        source.fps_num,
        source.fps_den,
        nested_tracks,
        source.audio_tracks,
        source_timeline_id,
        source.audio_sample_rate,
    )
    repo.create_timeline(nested)

    compound = new_compound_layer(
        timeline_id=nested_id,
        timeline_range=TimeRange(
            RationalTime.from_seconds(start),
            RationalTime.from_seconds(end),
        ),
        name=name,
    )

    tracks = tuple(
        track.with_layers(
            tuple(layer for layer in track.layers if layer.id not in selected_ids)
            + ((compound,) if track.id == source.video_tracks[0].id else ())
        )
        for track in source.video_tracks
    )
    repo._set(source.with_video_tracks(tracks))
    return nested_id, compound
