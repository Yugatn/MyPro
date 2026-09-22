from core.migration import Migration, MigrationRegistry


def test_migration_can_follow_registered_path():
    registry = MigrationRegistry()
    registry.register(Migration("v1", "v2", False, False, lambda d: {**d, "schema_version": "v2"}))
    registry.register(Migration("v2", "v3", False, False, lambda d: {**d, "schema_version": "v3"}))
    result = registry.migrate({"schema_version": "v1", "x": 1}, "v1", "v3")
    assert result["schema_version"] == "v3"
