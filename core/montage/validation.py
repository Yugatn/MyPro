"""Validation for legacy and Foundation v0.4 montage models."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import pairwise
from .model import MontageProject, Timeline


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    clip_id: str | None = None


def validate_project(project: MontageProject) -> list[ValidationIssue]:
    issues = []
    seen = set()
    for clip in project.clips:
        if clip.id in seen:
            issues.append(ValidationIssue("duplicate_clip_id", "Clip id is duplicated.", clip.id))
        seen.add(clip.id)
        if clip.start_seconds < 0:
            issues.append(
                ValidationIssue("negative_start", "Clip start cannot be negative.", clip.id)
            )
        if clip.end_seconds <= clip.start_seconds:
            issues.append(
                ValidationIssue("invalid_range", "Clip range is not positive.", clip.id)
            )
    return issues


class InvariantViolation(ValueError):
    pass


def validate_timeline(tl: Timeline) -> None:
    if tl.fps_num <= 0 or tl.fps_den <= 0:
        raise InvariantViolation("I_timeline_valid_fps")
    if tl.audio_sample_rate <= 0:
        raise InvariantViolation("I_timeline_valid_sample_rate")

    video_indices = [t.index for t in tl.video_tracks]
    if video_indices != list(range(len(video_indices))):
        raise InvariantViolation("I_track_index_unique")
    audio_indices = [t.index for t in tl.audio_tracks]
    if audio_indices != list(range(len(audio_indices))):
        raise InvariantViolation("I_track_index_unique")

    for track in tl.video_tracks:
        seen_ids = set()
        for layer in track.layers:
            if layer.id in seen_ids:
                raise InvariantViolation("I_layer_id_unique")
            seen_ids.add(layer.id)
            if layer.range.start.fraction < 0:
                raise InvariantViolation("I_layer_non_negative_time")

        ordered = sorted(track.layers, key=lambda x: x.range.start.fraction)
        for a, b in pairwise(ordered):
            if a.range.end.fraction > b.range.start.fraction:
                raise InvariantViolation("I_layer_no_overlap_on_track")


def validate_project_v2(timelines, media_pool) -> None:
    def visit(tid, stack):
        if tid in stack:
            raise InvariantViolation("I_timeline_no_cycle")
        if tid not in timelines:
            raise InvariantViolation("I_timeline_exists")
        tl = timelines[tid]
        validate_timeline(tl)
        for track in tl.video_tracks:
            for layer in track.layers:
                if layer.source_id and layer.source_id not in media_pool:
                    raise InvariantViolation("I_clip_source_exists")
                if layer.nested_timeline_id:
                    if layer.nested_timeline_id not in timelines:
                        raise InvariantViolation("I_compound_target_exists")
                    visit(layer.nested_timeline_id, stack | {tid})

    roots = [tid for tid, timeline in timelines.items() if timeline.parent_timeline_id is None]
    visited = set()
    for tid in roots:
        visit(tid, set())
        visited.add(tid)

    if not roots and timelines:
        raise InvariantViolation("I_project_has_root_timeline")
