from pathlib import Path

from core.backup import BackupStore
from core.identity import ContentHash
from core.project import Project


def test_backup_contains_project_files_and_restores(tmp_path: Path):
    project = Project.create(tmp_path / "project")
    project.append_event("test.created", {"value": 1})
    store = BackupStore(project.root)

    digest = store.create(event_log=project.log, snapshots=project.snapshots)
    package = project.root / "backups" / digest.hex / "project"

    assert (package / "manifest.json").exists()
    assert (package / "events.jsonl").exists()
    assert store.verify(event_log=project.log, snapshots=project.snapshots, digest=digest)

    destination = tmp_path / "restored"
    store.restore(target=destination, digest=digest, source_root=project.root)
    restored = Project(destination)
    assert restored.log.count == project.log.count
