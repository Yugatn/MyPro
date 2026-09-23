"""Content-addressed identity primitives for MyPro Foundation v0.4."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Any

try:
    import blake3
except ImportError:
    blake3 = None


@dataclass(frozen=True)
class ContentHash:
    algorithm: str
    digest: bytes

    def __post_init__(self) -> None:
        if not self.algorithm:
            raise ValueError("hash algorithm must not be empty")
        if not self.digest:
            raise ValueError("hash digest must not be empty")

    def __str__(self) -> str:
        return f"{self.algorithm}:{self.digest.hex()}"

    @property
    def hex(self) -> str:
        return self.digest.hex()

    @classmethod
    def parse(cls, value: str) -> "ContentHash":
        if ":" not in value:
            raise ValueError("content hash must use algorithm:hex format")
        algorithm, encoded = value.split(":", 1)
        if not algorithm or not encoded:
            raise ValueError("invalid content hash")
        try:
            digest = bytes.fromhex(encoded)
        except ValueError as exc:
            raise ValueError("invalid content hash hex") from exc
        return cls(algorithm, digest)


def _validate_json(value: Any) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("non-finite floats are not allowed in canonical data")
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("canonical JSON object keys must be strings")
            _validate_json(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _validate_json(item)


def canonical_bytes(value: Any) -> bytes:
    _validate_json(value)
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def hash_bytes(data: bytes, algorithm: str = "blake3") -> ContentHash:
    if algorithm == "blake3":
        if blake3 is None:
            raise RuntimeError("blake3 dependency is required for blake3 hashes")
        digest = blake3.blake3(data).digest()
    elif algorithm == "sha256":
        digest = hashlib.sha256(data).digest()
    else:
        raise ValueError(f"unsupported hash algorithm: {algorithm}")
    return ContentHash(algorithm, digest)


def hash_canonical(value: Any, algorithm: str = "blake3") -> ContentHash:
    return hash_bytes(canonical_bytes(value), algorithm=algorithm)
