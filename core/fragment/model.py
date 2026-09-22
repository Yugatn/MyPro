"""Canonical semantic/editorial fragment model."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping
from core.project.time import TimeRange

class FragmentKind(str, Enum):
    MEDIA = "media"
    SCENE = "scene"
    SPEECH = "speech"
    ACTION = "action"
    REACTION = "reaction"
    OBJECT = "object"
    PERSON = "person"
    SOUND = "sound"
    SEMANTIC = "semantic"
    COMPOSITE = "composite"

class FragmentStatus(str, Enum):
    CANDIDATE = "candidate"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

@dataclass(frozen=True)
class ContentFragment:
    id: str
    source_content_id: str
    source_hash: str
    time_range: TimeRange
    kind: FragmentKind
    observation_ids: tuple[str, ...] = ()
    confidence: float | None = None
    uncertainty: float | None = None
    detector_id: str | None = None
    detector_version: str | None = None
    label: str | None = None
    attributes: Mapping[str, Any] = field(default_factory=dict)
    status: FragmentStatus = FragmentStatus.CANDIDATE
    parent_fragment_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.source_content_id or not self.source_hash:
            raise ValueError("fragment source identity is required")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.uncertainty is not None and not 0.0 <= self.uncertainty <= 1.0:
            raise ValueError("uncertainty must be between 0 and 1")
        if self.kind is FragmentKind.COMPOSITE and not self.parent_fragment_ids:
            raise ValueError("composite fragments require parent fragments")

@dataclass(frozen=True)
class FragmentProposal:
    id: str
    fragment_ids: tuple[str, ...]
    purpose: str
    created_by: str
    rationale: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.fragment_ids:
            raise ValueError("proposal requires at least one fragment")
        if not self.purpose.strip():
            raise ValueError("proposal purpose is required")
