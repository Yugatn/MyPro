from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol
from core.identity import ContentHash
from .manifest import ImportManifest


@dataclass(frozen=True)
class SourceDescriptor:
    path: str
    content_hash: ContentHash
    format: str
    version: str | None = None


@dataclass(frozen=True)
class ImportResult:
    adapter_id: str
    adapter_version: str
    source: SourceDescriptor
    canonical_project: dict[str,Any]
    manifest: ImportManifest
    mapping_report: tuple[dict[str,Any], ...] = ()
    provenance: tuple[dict[str,Any], ...] = ()

    def as_dict(self):
        return {
            "adapter_id":self.adapter_id,"adapter_version":self.adapter_version,
            "source":{"path":self.source.path,"content_hash":str(self.source.content_hash),
                      "format":self.source.format,"version":self.source.version},
            "canonical_project":self.canonical_project,
            "manifest":self.manifest.as_dict(),
            "mapping_report":list(self.mapping_report),
            "provenance":list(self.provenance),
        }


class ImportAdapter(Protocol):
    adapter_id: str
    adapter_version: str
    supported_extensions: tuple[str,...]

    def import_project(self, path: Path) -> ImportResult: ...
