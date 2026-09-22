"""Import adapters produce evidence and never mutate a project."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..identity import new_id
from .reports import ImportManifest


@dataclass(frozen=True, slots=True)
class ImportResult:
    id: str
    adapter_id: str
    adapter_version: str
    manifest: ImportManifest
    canonical_candidate: dict[str, Any]
    observations: tuple[dict[str, Any], ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "adapter_id": self.adapter_id,
            "adapter_version": self.adapter_version,
            "manifest": self.manifest.as_dict(),
            "canonical_candidate": self.canonical_candidate,
            "observations": list(self.observations),
        }


class ImportAdapter(ABC):
    adapter_id: str
    adapter_version: str
    source_format: str
    supported_extensions: tuple[str, ...]

    @abstractmethod
    def import_project(self, path: Path) -> ImportResult:
        raise NotImplementedError

    def _new_result(self, *, manifest: ImportManifest, canonical_candidate: dict[str, Any],
                    observations: tuple[dict[str, Any], ...] = ()) -> ImportResult:
        return ImportResult(
            id=new_id("import"), adapter_id=self.adapter_id, adapter_version=self.adapter_version,
            manifest=manifest, canonical_candidate=canonical_candidate, observations=observations,
        )
