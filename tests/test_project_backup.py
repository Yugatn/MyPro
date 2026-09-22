from pathlib import Path
from core.backup import BackupStore
from core.project import Project


def test_backup_and_verify(tmp_path: Path):
    project = Project.create(tmp_path / "project")
    project.append_event("test.event", {"value": 1})
    store = BackupStore(project.root)
    digest = store.create(event_log=project.log, snapshots=project.snapshots, label="test")
    assert store.verify(event_log=project.log, snapshots=project.snapshots, digest=digest)


def test_restore(tmp_path: Path):
    project = Project.create(tmp_path / "project")
    project.append_event("test.event", {"value": 1})
    store = BackupStore(project.root)
    digest = store.create(event_log=project.log, snapshots=project.snapshots, label="test")
    target = tmp_path / "restored"
    store.restore(target=target, digest=digest, source_root=project.root)
    restored = Project(target)
    assert restored.log.count >= project.log.count
