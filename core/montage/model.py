"""Canonical layered montage model.

The legacy Clip/MontageProject types remain for compatibility. Foundation v0.4
adds immutable rational-time layered primitives used by the repository.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from enum import Enum
from typing import Any
import json

from core.identity import ContentHash, hash_canonical, new_id if False else hash_canonical
from core.project.time import RationalTime, TimeRange


@dataclass(frozen=True)
class Clip:
    id: str
    media_id: str
    start_seconds: float
    end_seconds: float
    track: str = "video"


@dataclass
class MontageProject:
    version: str = "0.1"
    name: str = "Untitled"
    clips: list[Clip] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_clip(self, clip: Clip) -> None:
        if clip.end_seconds <= clip.start_seconds:
            raise ValueError("Clip end must be greater than clip start.")
        if any(existing.id == clip.id for existing in self.clips):
            raise ValueError(f"Duplicate clip id: {clip.id}")
        self.clips.append(clip)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["clips"] = [asdict(clip) for clip in self.clips]
        return data

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


class LayerKind(str, Enum):
    CLIP = "clip"
    ADJUSTMENT = "adjustment"
    COMPOUND = "compound"


@dataclass(frozen=True)
class MediaAsset:
    id: str
    name: str
    content_hash: ContentHash
    kind: str
    duration: RationalTime
    width: int | None = None
    height: int | None = None
    fps_num: int | None = None
    fps_den: int | None = None


@dataclass(frozen=True)
class VideoLayer:
    id: str
    kind: LayerKind
    name: str
    range: TimeRange
    source_id: str | None = None
    nested_timeline_id: str | None = None

    def with_range(self, value: TimeRange) -> "VideoLayer":
        return replace(self, range=value)


@dataclass(frozen=True)
class AudioLayer:
    id: str
    name: str
    range: TimeRange
    source_id: str | None = None


@dataclass(frozen=True)
class VideoTrack:
    id: str
    index: int
    name: str
    layers: tuple[VideoLayer, ...] = ()

    def with_layers(self, layers: tuple[VideoLayer, ...]) -> "VideoTrack":
        return replace(self, layers=layers)


@dataclass(frozen=True)
class AudioTrack:
    id: str
    index: int
    name: str
    layers: tuple[AudioLayer, ...] = ()

    def with_layers(self, layers: tuple[AudioLayer, ...]) -> "AudioTrack":
        return replace(self, layers=layers)


@dataclass(frozen=True)
class Timeline:
    id: str
    name: str
    fps_num: int
    fps_den: int
    video_tracks: tuple[VideoTrack, ...]
    audio_tracks: tuple[AudioTrack, ...]
    parent_timeline_id: str | None = None
    audio_sample_rate: int = 48000

    @property
    def duration(self) -> RationalTime:
        ranges = [l.range for t in self.video_tracks for l in t.layers]
        ranges += [l.range for t in self.audio_tracks for l in t.layers]
        return max((r.end for r in ranges), default=RationalTime(0, 1))

    def with_video_tracks(self, tracks: tuple[VideoTrack, ...]) -> "Timeline":
        return replace(self, video_tracks=tracks)

    def with_audio_tracks(self, tracks: tuple[AudioTrack, ...]) -> "Timeline":
        return replace(self, audio_tracks=tracks)


def _id(prefix: str) -> str:
    import uuid
    return f"{prefix}_{uuid.uuid4().hex}"


def new_clip_layer(*, asset_id: str, timeline_range: TimeRange, name: str | None = None) -> VideoLayer:
    return VideoLayer(_id("vl"), LayerKind.CLIP, name or asset_id, timeline_range, source_id=asset_id)


def new_compound_layer(*, timeline_id: str, timeline_range: TimeRange, name: str | None = None) -> VideoLayer:
    return VideoLayer(_id("vl"), LayerKind.COMPOUND, name or "compound", timeline_range,
                      nested_timeline_id=timeline_id)


def new_timeline(name: str, *, fps_num: int = 24, fps_den: int = 1,
                 default_video_tracks: int = 2, default_audio_tracks: int = 2,
                 parent_timeline_id: str | None = None) -> Timeline:
    if default_video_tracks < 1 or default_audio_tracks < 0:
        raise ValueError("invalid default track count")
    return Timeline(
        id=_id("tl"), name=name, fps_num=fps_num, fps_den=fps_den,
        video_tracks=tuple(VideoTrack(_id("vt"), i, f"V{i+1}") for i in range(default_video_tracks)),
        audio_tracks=tuple(AudioTrack(_id("at"), i, f"A{i+1}") for i in range(default_audio_tracks)),
        parent_timeline_id=parent_timeline_id,
    )
