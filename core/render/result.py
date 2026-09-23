"""Renderer result and provenance artifact."""
from __future__ import annotations

from dataclasses import dataclass

from core.identity import ContentHash, hash_canonical


@dataclass(frozen=True)
class RenderResult:
    specification_hash: ContentHash
    output_path: str
    command: tuple[str, ...]
    executed: bool
    return_code: int | None = None
    output_hash: ContentHash | None = None
    stderr: str = ""

    def to_dict(self) -> dict:
        return {
            "specification_hash": str(self.specification_hash),
            "output_path": self.output_path,
            "command": list(self.command),
            "executed": self.executed,
            "return_code": self.return_code,
            "output_hash": str(self.output_hash) if self.output_hash else None,
            "stderr": self.stderr,
        }

    @property
    def provenance_hash(self):
        return hash_canonical(self.to_dict())
