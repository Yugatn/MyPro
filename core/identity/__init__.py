"""Content-addressed identity primitives for MyPro Foundation v0.4."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

try:
    import blake3 as _blake3
except ImportError:  # pragma: no cover
    _blake3 = None

SUPPORTED_ALGORITHMS = {"sha256", "blake3"}


@dataclass(frozen=True, order=True)
class ContentHash:
    algorithm: str
    hex: str

    def __post_init__(self) -> None:
        if self.algorithm not in SUPPORTED_ALGORITHMS:
            raise ValueError(f"unsupported hash algorithm: {self.algorithm}")
        if len(self.hex) != 64 or any(c not in "0123456789abcdef" for c in self.hex.lower()):
            raise ValueError("hash must be a 64-character lowercase hexadecimal digest")
        object.__setattr__(self, "hex", self.hex.lower())

    def __str__(self) -> str:
        return f"{self.algorithm}:{self.hex}"

    @classmethod
    def parse(cls, value: str) -> "ContentHash":
        algorithm, sep, digest = value.partition(":")
        if not sep:
            raise ValueError("content hash must be '<algorithm>:<hex>'")
        return cls(algorithm, digest)


def hash_bytes(data: bytes, *, algorithm: str = "blake3") -> ContentHash:
    if algorithm == "sha256":
        digest = hashlib.sha256(data).hexdigest()
    elif algorithm == "blake3":
        if _blake3 is None:
            raise RuntimeError("blake3 package is required for blake3 hashing")
        digest = _blake3.blake3(data).hexdigest()
    else:
        raise ValueError(f"unsupported hash algorithm: {algorithm}")
    return ContentHash(algorithm, digest)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def hash_canonical(value: Any, *, algorithm: str = "blake3") -> ContentHash:
    return hash_bytes(canonical_bytes(value), algorithm=algorithm)
