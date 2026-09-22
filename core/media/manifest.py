"""Minimal, dependency-free media manifest model."""

from dataclasses import asdict, dataclass, field
from typing import Any
import json


@dataclass(frozen=True)
class MediaFile:
    id: str
    path: str
    kind: str = "video"
    duration_seconds: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MediaManifest:
    version: str = "0.1"
    media: list[MediaFile] = field(default_factory=list)

    def add(self, item: MediaFile) -> None:
        if any(existing.id == item.id for existing in self.media):
            raise ValueError(f"Duplicate media id: {item.id}")
        self.media.append(item)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "media": [item.to_dict() for item in self.media],
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
