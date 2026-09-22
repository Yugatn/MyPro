"""Deterministic schema migration registry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .errors import MigrationError

MigrationFn = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True)
class Migration:
    source_version: str
    target_version: str
    reversible: bool
    lossy: bool
    migrate: MigrationFn
    rollback: MigrationFn | None = None


class MigrationRegistry:
    def __init__(self) -> None:
        self._migrations: dict[tuple[str, str], Migration] = {}

    def register(self, migration: Migration) -> None:
        key = (migration.source_version, migration.target_version)
        if key in self._migrations:
            raise MigrationError(f"migration already registered: {key}")
        if migration.reversible and migration.rollback is None:
            raise MigrationError("reversible migration requires rollback")
        self._migrations[key] = migration

    def migrate(self, document: dict[str, Any], source_version: str, target_version: str) -> dict[str, Any]:
        if source_version == target_version:
            if document.get("schema_version") not in (None, target_version):
                raise MigrationError("document schema_version conflicts with source_version")
            result = dict(document)
            result["schema_version"] = target_version
            return result

        current = source_version
        result = dict(document)
        visited: set[str] = set()
        while current != target_version:
            if current in visited:
                raise MigrationError(f"migration cycle detected at {current}")
            visited.add(current)
            candidates = [
                migration for (src, _), migration in self._migrations.items()
                if src == current
            ]
            if not candidates:
                raise MigrationError(f"no migration path from {current} to {target_version}")
            direct = [m for m in candidates if m.target_version == target_version]
            if len(candidates) > 1 and len(direct) != 1:
                raise MigrationError(f"ambiguous migration path from {current}")
            migration = direct[0] if direct else candidates[0]
            result = migration.migrate(dict(result))
            if result.get("schema_version") != migration.target_version:
                raise MigrationError(
                    f"migration produced wrong version: expected {migration.target_version}"
                )
            current = migration.target_version
        return result
