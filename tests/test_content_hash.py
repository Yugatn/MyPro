from pathlib import Path
import pytest
from core.identity import ContentHash, hash_bytes, hash_file


def test_algorithm_is_part_of_identity():
    digest = hash_bytes(b"hello")
    assert digest.algorithm == "blake3"
    assert ContentHash.parse(str(digest)) == digest


def test_sha256_and_blake3_are_distinct():
    assert hash_bytes(b"hello", algorithm="sha256") != hash_bytes(b"hello", algorithm="blake3")


def test_file_hash(tmp_path: Path):
    path = tmp_path / "data.bin"
    path.write_bytes(b"hello")
    assert hash_file(path).hex


def test_invalid_algorithm():
    with pytest.raises(ValueError):
        ContentHash("md5", "0" * 64)
