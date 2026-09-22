"""Versioned observation model and analyzer identity."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


ObservationStatus = Literal["observed", "not_analyzed", "failed", "unknown"]


@dataclass(frozen=True)
class AnalyzerIdentity:
    analyzer_id: str
    version: str
    code_hash: str | None = None
    config_hash: str | None = None


@dataclass(frozen=True)
class Observation:
    id: str
    type: str
    asset_id: str
    value: Any
    confidence: float
    uncertainty: Any
    status: ObservationStatus
    provenance_id: str | None = None
    analyzer: AnalyzerIdentity | None = None
    schema_version: str = "0.2"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if not self.id or not self.type or not self.asset_id:
            raise ValueError("id, type and asset_id are required")

    def to_dict(self) -> dict[str, Any]:
        analyzer = None
        if self.analyzer:
            analyzer = {
                "analyzer_id": self.analyzer.analyzer_id,
                "version": self.analyzer.version,
                "code_hash": self.analyzer.code_hash,
                "config_hash": self.analyzer.config_hash,
            }
        return {
            "id": self.id,
            "type": self.type,
            "asset_id": self.asset_id,
            "value": self.value,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "status": self.status,
            "provenance_id": self.provenance_id,
            "analyzer": analyzer,
            "schema_version": self.schema_version,
            "metadata": self.metadata,
        }
