from pathlib import Path

import pytest

from core.import_layer import (
    ImportManifest, ImportProposal, ImportResult, ImportService,
    LossReport, MappingReport, RelinkingReport, SourceDescriptor,
)
from core.project import Project


def make_result() -> ImportResult:
    source = SourceDescriptor(
        "test", None, "adapter", "1.0", "blake3:" + "0" * 64, 1, "now"
    )
    manifest = ImportManifest(source, MappingReport(), LossReport(), RelinkingReport())
    return ImportResult("import-1", "adapter", "1.0", manifest, {"tracks": []})


def test_import_apply_requires_recorded_approval(tmp_path: Path):
    project = Project.create(tmp_path / "project")
    result = make_result()
    service = ImportService()
    proposal = service.propose(project, result)

    with pytest.raises(PermissionError):
        service.apply(project, proposal, result, approved=True)

    service.decide(project, proposal, approved=True)
    revision = service.apply(project, proposal, result, approved=True)
    assert revision.startswith("revision_")
