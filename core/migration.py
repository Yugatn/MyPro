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
        migration = self._migrations.get((source_version, target_version))
        if migration is None:
            raise MigrationError(f"unsupported migration: {source_version} to {target_version}")
        result = migration.migrate(dict(document))
        if result.get("schema_version") != target_version:
            raise MigrationError("migration produced the wrong target version")
        return result
