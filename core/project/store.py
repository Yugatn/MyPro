"""Project v0.3 persistence boundary."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from ..identity import new_id
from .events import EventLog, SnapshotStore

PROJECT_SCHEMA_VERSION = "project.v2"


@dataclass(frozen=True, slots=True)
class ProjectManifest:
    project_id: str
    schema_version: str = PROJECT_SCHEMA_VERSION
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.created_at:
            object.__setattr__(
                self, "created_at",
                datetime.now(timezone.utc).isoformat(timespec="microseconds"),
            )

    def to_dict(self) -> dict:
        return {
            "format": "mypro",
            "project_id": self.project_id,
            "schema_version": self.schema_version,
            "created_at": self.created_at,
            "event_log": "events.jsonl",
            "snapshot_head": None,
        }


class Project:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.root / "manifest.json"
        self.log = EventLog(self.root / "events.jsonl")
        self.snapshots = SnapshotStore(self.root / "snapshots")
        self.backups_dir = self.root / "backups"
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        self.provenance_dir = self.root / "provenance"
        self.provenance_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def create(cls, root: str | Path) -> "Project":
        project = cls(root)
        if not project.manifest_path.exists():
            project._write_manifest(ProjectManifest(project_id=new_id("proj")))
            project.append_event(
                "project.created",
                {"project_id": project.read_manifest().project_id},
            )
        return project

    def _write_manifest(self, manifest: ProjectManifest) -> None:
        temp = self.manifest_path.with_name(f".{self.manifest_path.name}.tmp")
        data = json.dumps(manifest.to_dict(), indent=2, sort_keys=True).encode()
        with temp.open("wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, self.manifest_path)
        dir_fd = os.open(self.root, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)

    def read_manifest(self) -> ProjectManifest:
        data = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        return ProjectManifest(data["project_id"], data["schema_version"], data["created_at"])

    def append_event(self, event_type: str, payload: dict, *, actor: str = "system"):
        return self.log.append_new(
            event_id=new_id("evt"),
            event_type=event_type,
            payload=payload,
            actor=actor,
        )

    def snapshot(self, state: dict) -> str:
        return str(self.snapshots.write({
            "project_id": self.read_manifest().project_id,
            "schema_version": PROJECT_SCHEMA_VERSION,
            "tip_hash": self.log.tip_hash,
            "event_count": self.log.count,
            "state": state,
        }))
