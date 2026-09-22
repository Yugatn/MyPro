"""Content-addressed provenance records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..identity import ContentHash, hash_canonical


@dataclass(frozen=True, slots=True)
class ProvenanceNode:
    id: str
    operation: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    software: str
    code_hash: str | None = None
    config_hash: str | None = None
    parent_ids: tuple[str, ...] = ()
    created_at: str = ""

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "id": self.id, "operation": self.operation,
            "inputs": list(self.inputs), "outputs": list(self.outputs),
            "software": self.software, "code_hash": self.code_hash,
            "config_hash": self.config_hash, "parent_ids": list(self.parent_ids),
            "created_at": self.created_at,
        }

    @property
    def content_hash(self) -> ContentHash:
        return hash_canonical(self.canonical_payload())


def verify_provenance(nodes: dict[str, ProvenanceNode]) -> bool:
    return all(parent in nodes for node in nodes.values() for parent in node.parent_ids)
