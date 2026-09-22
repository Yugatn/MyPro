from pathlib import Path

from core.project.events import SnapshotStore


def test_snapshot_supports_non_default_hash_algorithm(tmp_path: Path):
    store = SnapshotStore(tmp_path)
    digest = store.write({"x": 1}, algorithm="sha256")
    assert digest.algorithm == "sha256"
    assert store.read(digest) == {"x": 1}
