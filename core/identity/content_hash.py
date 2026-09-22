"""Content-addressed identity with explicit hash algorithms."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

import blake3
import ulid

DEFAULT_ALGORITHM: Final[str] = "blake3"
SUPPORTED_ALGORITHMS: Final[frozenset[str]] = frozenset({"blake3", "sha256"})


@dataclass(frozen=True, slots=True)
class ContentHash:
    algorithm: str
    hex: str

    def __post_init__(self) -> None:
        if self.algorithm not in SUPPORTED_ALGORITHMS:
            raise ValueError(f"unsupported algorithm: {self.algorithm}")
        if not self.hex or any(c not in "0123456789abcdef" for c in self.hex):
            raise ValueError("digest must be lowercase hexadecimal")
        if len(self.hex) != 64:
            raise ValueError("digest must contain 64 hex characters")

    def __str__(self) -> str:
        return f"{self.algorithm}:{self.hex}"

    @classmethod
    def parse(cls, value: str) -> "ContentHash":
        algorithm, separator, digest = value.partition(":")
        if not separator:
            raise ValueError("ContentHash must use 'algorithm:hex' form")
        return cls(algorithm, digest)


def _hasher(algorithm: str):
    if algorithm == "blake3":
        return blake3.blake3()
    if algorithm == "sha256":
        return hashlib.sha256()
    raise ValueError(f"unsupported algorithm: {algorithm}")


def hash_bytes(data: bytes, *, algorithm: str = DEFAULT_ALGORITHM) -> ContentHash:
    hasher = _hasher(algorithm)
    hasher.update(data)
    return ContentHash(algorithm, hasher.hexdigest())


def hash_file(path: Path, *, algorithm: str = DEFAULT_ALGORITHM, chunk_size: int = 1 << 20) -> ContentHash:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    hasher = _hasher(algorithm)
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            hasher.update(chunk)
    return ContentHash(algorithm, hasher.hexdigest())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False,
    ).encode("utf-8")


def hash_canonical(value: Any, *, algorithm: str = DEFAULT_ALGORITHM) -> ContentHash:
    return hash_bytes(canonical_bytes(value), algorithm=algorithm)


def new_id(prefix: str = "id") -> str:
    return f"{prefix}_{ulid.new().str}"
