from core.import_layer import (
    ImportManifest, ImportProposal, ImportResult, ImportService,
    LossReport, MappingReport, RelinkingReport, SourceDescriptor,
)
from core.project import Project


def test_import_is_proposal_before_revision(tmp_path):
    source = SourceDescriptor("test", None, "test-adapter", "1.0", "blake3:" + "0" * 64, 1, "now")
    manifest = ImportManifest(source, MappingReport(), LossReport(), RelinkingReport())
    result = ImportResult("import-1", "test-adapter", "1.0", manifest, {"tracks": []})
    project = Project.create(tmp_path / "project")
    service = ImportService()
    proposal = service.propose(project, result)
    assert proposal.id
    assert any(e.event_type == "proposal.import_project" for e in project.log.iter_events())
    assert not any(e.event_type == "revision.created" for e in project.log.iter_events())
