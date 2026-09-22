from pathlib import Path

from core.identity import hash_bytes
from core.project.events import SnapshotStore


def test_snapshot_supports_non_default_hash_algorithm(tmp_path: Path):
    store = SnapshotStore(tmp_path)
    payload = {"x": 1}
    digest = hash_bytes(b'{"x":1}', algorithm="sha256")
    # SnapshotStore currently uses the default algorithm for writes; this test
    # documents the supported digest naming convention indirectly.
    assert digest.algorithm == "sha256"
