"""Analyzer contract with reproducible implementation identity."""

from __future__ import annotations

from abc import ABC, abstractmethod
import inspect
from pathlib import Path
from typing import Any, Iterable

from ..capability import CapabilityIssuer
from ..identity import ContentHash, hash_bytes, hash_canonical
from .model import AnalyzerIdentity, Observation


def source_code_hash(cls: type) -> ContentHash:
    parts: list[bytes] = []
    try:
        parts.append(inspect.getsource(cls).encode("utf-8"))
    except (OSError, TypeError):
        parts.append(repr(cls).encode("utf-8"))
    module = inspect.getmodule(cls)
    module_file = getattr(module, "__file__", None) if module else None
    if module_file:
        try:
            parts.append(Path(module_file).read_bytes())
        except OSError:
            pass
    return hash_bytes(b"\0".join(parts))


class Analyzer(ABC):
    analyzer_id: str
    version: str
    determinism_class: str = "deterministic"
    required_operations: frozenset[str] = frozenset()
    output_types: frozenset[str] = frozenset()
    config: dict[str, Any] = {}

    @property
    def identity(self) -> AnalyzerIdentity:
        return AnalyzerIdentity(
            analyzer_id=self.analyzer_id,
            version=self.version,
            code_hash=str(source_code_hash(type(self))),
            config_hash=str(hash_canonical(self.config)),
        )

    def authorize(self, issuer: CapabilityIssuer, capability_id: str, resource: str) -> None:
        for operation in self.required_operations:
            issuer.check(capability_id, operation, resource)

    @abstractmethod
    def run(self, inputs: dict[str, Any]) -> Iterable[Observation]:
        raise NotImplementedError
