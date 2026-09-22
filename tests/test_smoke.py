import importlib


def test_project_imports():
    for module in ("core", "core.media", "core.montage"):
        assert importlib.import_module(module)
