"""Project container and persistence."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
from core.identity import ContentHash, hash_canonical
from .events import EventLog, SnapshotStore


@dataclass(frozen=True)
class ProjectManifest:
    schema_version: str
    project_id: str
    created_at: str

    def to_dict(self) -> dict[str, str]:
        return {"schema_version": self.schema_version, "project_id": self.project_id, "created_at": self.created_at}


class Project:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.log = EventLog(self.root / "events.jsonl")
        self.snapshots = SnapshotStore(self.root / "snapshots")
        self.backups_dir = self.root / "backups"
        self.backups_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def create(cls, root: str | Path) -> Project:
        root = Path(root)
        root.mkdir(parents=True, exist_ok=True)
        manifest = root / "manifest.json"
        if not manifest.exists():
            project_id = f"proj_{hash_canonical(str(root.resolve())).hex[:16]}"
            data = ProjectManifest("0.4", project_id, datetime.now(UTC).isoformat()).to_dict()
            tmp = manifest.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
            tmp.replace(manifest)
        return cls(root)

    def read_manifest(self) -> ProjectManifest:
        data = json.loads((self.root / "manifest.json").read_text(encoding="utf-8"))
        return ProjectManifest(**data)

    def backup(self, *, label: str = "manual") -> ContentHash:
        payload = {
            "manifest": self.read_manifest().to_dict(),
            "events": self.log.read_all(),
        }
        digest = self.snapshots.write(name=label, payload=payload)
        ref = self.backups_dir / f"{digest.hex}.ref"
        ref.write_text(str(digest), encoding="utf-8")
        return digest

    def verify_backup(self, digest: ContentHash) -> bool:
        try:
            self.snapshots.read(digest)
            return True
        except (FileNotFoundError, ValueError, RuntimeError):
            return False

    def restore_backup(self, digest: ContentHash, *, target: str | Path) -> "Project":
        payload = self.snapshots.read(digest)
        target = Path(target)
        if target.exists():
            raise FileExistsError(target)
        target.mkdir(parents=True)
        (target / "snapshots").mkdir()
        (target / "backups").mkdir()
        (target / "manifest.json").write_text(
            json.dumps(payload["manifest"], indent=2, sort_keys=True), encoding="utf-8"
        )
        with (target / "events.jsonl").open("w", encoding="utf-8") as handle:
            for event in payload["events"]:
                handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
        return Project(target)
