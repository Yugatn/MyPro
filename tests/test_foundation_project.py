from pathlib import Path

import pytest

from core.identity import ContentHash, hash_bytes
from core.project import Project


def test_project_backup_roundtrip_and_tamper_detection(tmp_path: Path):
    root = tmp_path / "project.mypro"
    project = Project.create(root)
    project.log.append(type="project.created", payload={"name": "demo"})

    digest = project.backup(label="test")
    assert project.verify_backup(digest)

    restored_root = tmp_path / "restored.mypro"
    restored = project.restore_backup(digest, target=restored_root)
    assert restored.read_manifest() == project.read_manifest()
    assert restored.log.tip_hash == project.log.tip_hash

    snapshot = restored.snapshots.directory / f"{digest.hex}.json"
    snapshot.write_text(snapshot.read_text(encoding="utf-8").replace('"name": "demo"', '"name": "tampered"'),
                         encoding="utf-8")
    assert not restored.verify_backup(digest)


def test_content_hash_supports_sha256():
    value = hash_bytes(b"hello", algorithm="sha256")
    assert isinstance(value, ContentHash)
    assert value.algorithm == "sha256"
    assert ContentHash.parse(str(value)) == value
