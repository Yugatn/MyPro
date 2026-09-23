"""Immutable render specification."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from core.identity import hash_canonical


@dataclass(frozen=True)
class RenderSpecification:
    timeline_id: str
    output_path: str
    width: int = 1920
    height: int = 1080
    fps_num: int = 24
    fps_den: int = 1
    video_codec: str = "libx264"
    pixel_format: str = "yuv420p"
    audio_policy: str = "reject"
    overwrite: bool = False

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("render dimensions must be positive")
        if self.fps_num <= 0 or self.fps_den <= 0:
            raise ValueError("render fps must be positive")
        if self.audio_policy not in {"reject", "copy", "mix"}:
            raise ValueError("unsupported audio policy")

    @property
    def fps(self) -> Fraction:
        return Fraction(self.fps_num, self.fps_den)

    def to_dict(self) -> dict:
        return {
            "timeline_id": self.timeline_id,
            "output_path": str(Path(self.output_path)),
            "width": self.width,
            "height": self.height,
            "fps_num": self.fps_num,
            "fps_den": self.fps_den,
            "video_codec": self.video_codec,
            "pixel_format": self.pixel_format,
            "audio_policy": self.audio_policy,
            "overwrite": self.overwrite,
        }

    @property
    def spec_hash(self):
        return hash_canonical(self.to_dict())
