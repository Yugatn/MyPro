"""Separated import evidence reports."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class SourceDescriptor:
    format_id: str
    format_version: str | None
    adapter_id: str
    adapter_version: str
    source_hash: str
    size_bytes: int
    detected_at: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class MappingEntry:
    source_kind: str
    source_id: str
    target_kind: str
    target_id: str | None
    confidence: float

    def __post_init__(self) -> None:
        if not 0 <= self.confidence <= 1:
            raise ValueError("mapping confidence must be between 0 and 1")

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class MappingReport:
    entries: tuple[MappingEntry, ...] = ()
    unmapped: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {"entries": [e.as_dict() for e in self.entries], "unmapped": list(self.unmapped)}


@dataclass(frozen=True, slots=True)
class LossEntry:
    element: str
    severity: str
    reason: str
    fallback: str | None = None
    confidence: float = 1.0

    def __post_init__(self) -> None:
        if self.severity not in {"minor", "major", "critical"}:
            raise ValueError("invalid loss severity")
        if not 0 <= self.confidence <= 1:
            raise ValueError("loss confidence must be between 0 and 1")

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class LossReport:
    entries: tuple[LossEntry, ...] = ()

    def has_critical(self) -> bool:
        return any(e.severity == "critical" for e in self.entries)

    def as_dict(self) -> dict[str, Any]:
        return {"entries": [e.as_dict() for e in self.entries]}


@dataclass(frozen=True, slots=True)
class RelinkEntry:
    source_path: str
    resolved_path: str | None
    method: str
    confidence: float
    status: str

    def __post_init__(self) -> None:
        if self.method not in {"exact_hash", "path_match", "filename_match", "manual", "none"}:
            raise ValueError("invalid relinking method")
        if self.status not in {"resolved", "unresolved", "placeholder"}:
            raise ValueError("invalid relinking status")

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RelinkingReport:
    entries: tuple[RelinkEntry, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {"entries": [e.as_dict() for e in self.entries]}


@dataclass(frozen=True, slots=True)
class ImportManifest:
    source: SourceDescriptor
    mapping: MappingReport
    losses: LossReport
    relinking: RelinkingReport
    statistics: dict[str, int] = field(default_factory=dict)
    provenance_id: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": self.source.as_dict(),
            "mapping": self.mapping.as_dict(),
            "losses": self.losses.as_dict(),
            "relinking": self.relinking.as_dict(),
            "statistics": dict(self.statistics),
            "provenance_id": self.provenance_id,
        }
