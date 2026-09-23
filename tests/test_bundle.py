import io
import tarfile
from pathlib import Path

from core.bundle import export_bundle, import_bundle, verify_bundle
from core.project import Project

def test_export_verify_import(tmp_path: Path) -> None:
    project = Project.create(tmp_path / "proj")
    project.log.append(type="a", payload={"x": 1})
    project.log.append(type="b", payload={"y": 2})

    bundle = tmp_path / "out.bundle.tar.gz"
    export_bundle(project.root, bundle)
    verification = verify_bundle(bundle)
    assert verification.ok, verification.problems
    assert verification.event_count == 2

    restored = tmp_path / "restored"
    import_bundle(bundle, restored)
    restored_project = Project(restored)
    assert sum(1 for _ in restored_project.log.iter_events()) == 2

def test_tampered_bundle_fails(tmp_path: Path) -> None:
    project = Project.create(tmp_path / "proj")
    project.log.append(type="a", payload={"x": 1})
    bundle = tmp_path / "out.bundle.tar.gz"
    export_bundle(project.root, bundle)

    members = {}
    with tarfile.open(bundle, "r:gz") as tar:
        for member in tar.getmembers():
            source = tar.extractfile(member)
            if source is not None:
                members[member.name] = source.read()

    members["project/events.jsonl"] = members["project/events.jsonl"].replace(
        b'"x":1', b'"x":2', 1
    )
    with tarfile.open(bundle, "w:gz") as tar:
        for name, data in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mtime = 0
            tar.addfile(info, io.BytesIO(data))

    verification = verify_bundle(bundle)
    assert not verification.ok
    assert any("hash" in problem or "chain" in problem for problem in verification.problems)
