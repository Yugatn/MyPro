import pytest
from core.migration import Migration, MigrationRegistry
from core.errors import MigrationError


def test_declared_migration():
    registry = MigrationRegistry()
    registry.register(Migration("0.2", "0.3", False, False,
                                lambda doc: {**doc, "schema_version": "0.3"}))
    assert registry.migrate({"x": 1}, "0.2", "0.3")["schema_version"] == "0.3"


def test_unsupported_migration_fails_closed():
    with pytest.raises(MigrationError):
        MigrationRegistry().migrate({}, "0.2", "0.3")
