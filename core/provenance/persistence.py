"""Persistent provenance storage boundary."""

from __future__ import annotations

import json
from pathlib import Path

from ..identity import ContentHash
from ..project.events import EventLog
from .model import ProvenanceNode


class ProvenanceStore:
    def __init__(self, directory: str | Path, event_log: EventLog) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.event_log = event_log

    def put(self, node: ProvenanceNode, *, actor: str = "system") -> ContentHash:
        digest = node.content_hash
        target = self.directory / f"{digest.hex}.json"
        if not target.exists():
            target.write_text(
                json.dumps(node.canonical_payload(), sort_keys=True, separators=(",", ":")),
                encoding="utf-8",
            )
        self.event_log.append_new(
            event_id=f"prov_{node.id}",
            event_type="provenance.link",
            actor=actor,
            payload={"node_id": node.id, "node_hash": str(digest), "parent_ids": list(node.parent_ids)},
        )
        return digest

    def read(self, digest: ContentHash) -> ProvenanceNode:
        data = json.loads((self.directory / f"{digest.hex}.json").read_text(encoding="utf-8"))
        return ProvenanceNode(
            id=data["id"],
            operation=data["operation"],
            inputs=tuple(data["inputs"]),
            outputs=tuple(data["outputs"]),
            software=data["software"],
            code_hash=data.get("code_hash"),
            config_hash=data.get("config_hash"),
            parent_ids=tuple(data.get("parent_ids", ())),
            created_at=data.get("created_at", ""),
        )
