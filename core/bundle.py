"""Offline, content-addressed evidence bundle for a MyPro project."""
from __future__ import annotations
import io
import json
import tarfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from .errors import MyProError
from .identity import ContentHash, hash_file, hash_canonical
from .project import Project

BUNDLE_VERSION = "bundle.v1"

class BundleCorrupt(MyProError):
    pass

@dataclass(frozen=True, slots=True)
class BundleVerification:
    ok: bool
    bundle_hash: ContentHash
    project_id: str | None
    event_count: int
    tip_hash: str | None
    problems: tuple[str, ...]

def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds")

def _event_digest(event: dict[str, Any], previous: str | None) -> ContentHash:
    body = {
        "event_id": event["event_id"],
        "event_type": event["event_type"],
        "payload": event["payload"],
        "prev_hash": previous,
        "schema_version": event["schema_version"],
        "created_at": event["created_at"],
    }
    return hash_canonical(body)

def export_bundle(project_root: Path, output_path: Path, *, include_media: bool = False,
                  include_snapshots: bool = True) -> ContentHash:
    project = Project(project_root)
    manifest = project.read_manifest()
    events = project.log.read_all()
    media_refs: list[dict[str, Any]] = []

    manifest_data = {
        "bundle_version": BUNDLE_VERSION,
        "project_id": manifest.project_id,
        "project_schema": manifest.schema_version,
        "exported_at": _now(),
        "include_media": include_media,
        "include_snapshots": include_snapshots,
        "event_count": project.log.count,
        "tip_hash": str(project.log.tip_hash) if project.log.tip_hash else None,
    }

    repo_manifest = {
        "kind": "event_chain_root",
        "tip_hash": manifest_data["tip_hash"],
        "event_count": project.log.count,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(output_path, "w:gz") as tar:
        def add_bytes(name: str, data: bytes) -> None:
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            info.mtime = 0
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            tar.addfile(info, io.BytesIO(data))

        def add_json(name: str, value: Any) -> None:
            add_bytes(name, json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).encode())

        add_json("manifest.json", manifest_data)
        add_json("verification.json", {
            "algorithm": "replay event hash chain using project schema rules",
            "required": ["project/events.jsonl", "project/manifest.json", "manifest.json"],
        })
        add_json("media_references.json", media_refs)
        add_json("provenance_root.json", repo_manifest)
        add_bytes("project/events.jsonl", (project.root / "events.jsonl").read_bytes())
        add_bytes("project/manifest.json", (project.root / "manifest.json").read_bytes())

        if include_snapshots:
            snap_dir = project.root / "snapshots"
            if snap_dir.exists():
                for path in sorted(snap_dir.glob("*.json")):
                    add_bytes(f"project/snapshots/{path.name}", path.read_bytes())

    return hash_file(output_path)

def verify_bundle(bundle_path: Path) -> BundleVerification:
    problems: list[str] = []
    project_id = None
    event_count = 0
    tip_hash = None
    bundle_hash = hash_file(bundle_path)

    try:
        with tarfile.open(bundle_path, "r:gz") as tar:
            names = set(tar.getnames())
            required = {"manifest.json", "project/manifest.json", "project/events.jsonl"}
            missing = sorted(required - names)
            if missing:
                problems.extend(f"missing {name}" for name in missing)
            if problems:
                return BundleVerification(False, bundle_hash, None, 0, None, tuple(problems))

            manifest = json.loads(tar.extractfile("manifest.json").read())
            project_id = manifest.get("project_id")
            event_count = int(manifest.get("event_count") or 0)
            tip_hash = manifest.get("tip_hash")

            events_text = tar.extractfile("project/events.jsonl").read().decode("utf-8")
            previous = None
            actual_count = 0
            for line_no, raw in enumerate(events_text.splitlines(), start=1):
                if not raw.strip():
                    continue
                try:
                    event = json.loads(raw)
                except json.JSONDecodeError as exc:
                    problems.append(f"line {line_no}: invalid JSON: {exc}")
                    break
                expected = _event_digest(event, previous)
                actual = event.get("event_hash")
                if actual != str(expected):
                    problems.append(f"line {line_no}: event hash mismatch")
                    break
                if event.get("prev_hash") != previous:
                    problems.append(f"line {line_no}: chain break")
                    break
                previous = actual
                actual_count += 1

            if actual_count != event_count:
                problems.append(f"event_count mismatch: manifest={event_count} actual={actual_count}")
            if previous != tip_hash:
                problems.append(f"tip_hash mismatch: manifest={tip_hash} actual={previous}")
    except (OSError, tarfile.TarError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        problems.append(f"cannot verify bundle: {exc}")

    return BundleVerification(not problems, bundle_hash, project_id, event_count, tip_hash, tuple(problems))

def import_bundle(bundle_path: Path, target_root: Path) -> Project:
    verification = verify_bundle(bundle_path)
    if not verification.ok:
        raise BundleCorrupt("; ".join(verification.problems))
    if target_root.exists() and any(target_root.iterdir()):
        raise FileExistsError(target_root)
    target_root.mkdir(parents=True, exist_ok=True)
    with tarfile.open(bundle_path, "r:gz") as tar:
        for member in tar.getmembers():
            if not member.name.startswith("project/"):
                continue
            relative = member.name.removeprefix("project/")
            if not relative:
                continue
            destination = target_root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            source = tar.extractfile(member)
            if source is not None:
                destination.write_bytes(source.read())
    return Project(target_root)
