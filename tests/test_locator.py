from pathlib import Path
import pytest
from core.identity import hash_file
from core.media.locator import MediaHashMismatch, MediaLocator, UnresolvedMedia

def test_resolve_original(tmp_path: Path) -> None:
    path = tmp_path / "v.mp4"
    path.write_bytes(b"fake")
    locator = MediaLocator()
    locator.register("a1", path)
    resolved = locator.resolve("a1")
    assert resolved.path == path
    assert not resolved.is_proxy

def test_hash_verification(tmp_path: Path) -> None:
    path = tmp_path / "v.mp4"
    path.write_bytes(b"fake")
    locator = MediaLocator()
    locator.register("a1", path, expected_hash=hash_file(path))
    resolved = locator.resolve("a1", verify_hash=True)
    assert resolved.hash_verified

def test_hash_mismatch_detected(tmp_path: Path) -> None:
    path = tmp_path / "v.mp4"
    path.write_bytes(b"fake")
    different = tmp_path / "different"
    different.write_bytes(b"other")
    locator = MediaLocator()
    locator.register("a1", path, expected_hash=hash_file(different))
    with pytest.raises(MediaHashMismatch):
        locator.resolve("a1", verify_hash=True)

def test_proxy_fallback(tmp_path: Path) -> None:
    locator = MediaLocator()
    locator.register("a1", tmp_path / "missing.mp4")
    proxy = tmp_path / "proxy.mp4"
    proxy.write_bytes(b"proxy")
    locator.register_proxy("a1", proxy)
    resolved = locator.resolve("a1")
    assert resolved.is_proxy

def test_unresolved_raises(tmp_path: Path) -> None:
    locator = MediaLocator()
    locator.register("a1", tmp_path / "missing.mp4")
    with pytest.raises(UnresolvedMedia):
        locator.resolve("a1")
