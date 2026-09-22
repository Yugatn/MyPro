from core.identity import ContentHash, hash_bytes, hash_canonical
import pytest

def test_algorithm_aware_hash():
    h=hash_bytes(b"hello")
    assert h.algorithm=="blake3" and str(h).startswith("blake3:")

def test_roundtrip():
    h=hash_bytes(b"hello")
    assert ContentHash.parse(str(h))==h

def test_canonical_stable():
    assert hash_canonical({"b":2,"a":1})==hash_canonical({"a":1,"b":2})

def test_nan_rejected():
    with pytest.raises(ValueError): hash_canonical({"x":float("nan")})
