"""Minimal canonical montage model."""

from dataclasses import asdict, dataclass, field
from typing import Any
import json


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
