from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class LossyTransformation:
    element: str
    reason: str
    severity: str = "minor"
    fallback: str | None = None


@dataclass(frozen=True)
class Ambiguity:
    element: str
    reason: str
    confidence: float


@dataclass(frozen=True)
class UnmappedMedia:
    source_path: str
    status: str
    action: str


@dataclass
class ImportManifest:
    adapter_id: str
    adapter_version: str
    source_format: str
    source_version: str | None
    source_hash: str
    imported_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    statistics: dict[str,int] = field(default_factory=dict)
    losses: list[LossyTransformation] = field(default_factory=list)
    ambiguities: list[Ambiguity] = field(default_factory=list)
    unmapped_media: list[UnmappedMedia] = field(default_factory=list)
    mapping_rules_applied: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str,Any]:
        return asdict(self)

    def has_critical_loss(self) -> bool:
        return any(x.severity=="critical" for x in self.losses)
