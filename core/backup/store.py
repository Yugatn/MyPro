"""Verified project backups and safe point-in-time restore."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from ..errors import BackupVerificationError
from ..identity import ContentHash, hash_canonical
from ..project.events import EventLog, SnapshotStore


class BackupStore:
    def __init__(self, project_root: str | Path) -> None:
        self.root = Path(project_root)
        self.backups = self.root / "backups"
        self.backups.mkdir(parents=True, exist_ok=True)

    def create(self, *, event_log: EventLog, snapshots: SnapshotStore, label: str = "manual") -> ContentHash:
        payload = {
            "format": "mypro-backup",
            "version": "0.3",
            "label": label,
            "event_count": event_log.count,
            "tip_hash": event_log.tip_hash,
        }
        digest = snapshots.write(payload, name="backup")
        package = self.backups / digest.hex
        package.mkdir(parents=True, exist_ok=True)
        project_copy = package / "project"
        project_copy.mkdir(parents=True, exist_ok=True)
        if any(project_copy.iterdir()):
            return digest
        if not project_copy.exists():
            for child in self.root.iterdir():
                if child.name == "backups":
                    continue
                destination = project_copy / child.name
                if child.is_dir():
                    shutil.copytree(child, destination)
                else:
                    shutil.copy2(child, destination)
        (package / "manifest.json").write_text(
            json.dumps({"digest": str(digest), "payload_hash": str(hash_canonical(payload))}, indent=2),
            encoding="utf-8",
        )
        return digest

    def verify(self, *, event_log: EventLog, snapshots: SnapshotStore, digest: ContentHash) -> bool:
        try:
            payload = snapshots.read(digest)
        except (FileNotFoundError, json.JSONDecodeError):
            return False
        if payload.get("format") != "mypro-backup":
            return False
        expected_count = int(payload.get("event_count", 0))
        if expected_count == 0:
            return payload.get("tip_hash") is None
        previous = None
        for index, event in enumerate(event_log.iter_events(), start=1):
            previous = event.event_hash
            if index == expected_count:
                return previous == payload.get("tip_hash")
        return False

    def restore(self, *, target: str | Path, digest: ContentHash, source_root: str | Path) -> Path:
        destination = Path(target)
        if destination.exists():
            raise BackupVerificationError(f"restore target already exists: {destination}")
        package = Path(source_root) / "backups" / digest.hex / "project"
        if not package.exists():
            raise BackupVerificationError(f"backup package missing: {digest}")
        shutil.copytree(package, destination)
        return destination
