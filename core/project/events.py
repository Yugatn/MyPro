"""Durable append-only event log and atomic snapshots."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Iterator

from ..errors import EventLogCorrupt
from ..identity import ContentHash, hash_bytes, hash_canonical

SCHEMA_VERSION = "event.v3"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


@dataclass(frozen=True, slots=True)
class ProjectEvent:
    event_id: str
    event_type: str
    payload: dict[str, Any]
    schema_version: str = SCHEMA_VERSION
    created_at: str = ""
    actor: str = "system"
    prev_hash: str | None = None
    event_hash: str | None = None

    def __post_init__(self) -> None:
        if not self.created_at:
            object.__setattr__(self, "created_at", _utc_now_iso())

    def unsigned_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "payload": self.payload,
            "schema_version": self.schema_version,
            "created_at": self.created_at,
            "actor": self.actor,
            "prev_hash": self.prev_hash,
        }

    def computed_hash(self) -> str:
        return str(hash_canonical(self.unsigned_dict()))

    def finalized(self) -> "ProjectEvent":
        return ProjectEvent(**self.unsigned_dict(), event_hash=self.computed_hash())

    def to_dict(self) -> dict[str, Any]:
        event = self.finalized() if self.event_hash is None else self
        data = event.unsigned_dict()
        data["event_hash"] = event.event_hash
        return data


class EventLog:
    """Append-only JSONL with hash chaining and crash-tail recovery."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._tip_hash: str | None = None
        self._count = 0
        self.recover()

    def recover(self) -> None:
        if not self.path.exists() or self.path.stat().st_size == 0:
            self._tip_hash = None
            self._count = 0
            return
        raw = self.path.read_bytes()
        if not raw.endswith(b"\n"):
            last_newline = raw.rfind(b"\n")
            if last_newline < 0:
                self.path.write_bytes(b"")
            else:
                with self.path.open("r+b") as handle:
                    handle.truncate(last_newline + 1)
                    handle.flush()
                    os.fsync(handle.fileno())
        tip = None
        count = 0
        for event in self.iter_events():
            tip, count = event.event_hash, count + 1
        self._tip_hash, self._count = tip, count

    def append(self, event: ProjectEvent) -> ProjectEvent:
        finalized = event.finalized()
        if finalized.prev_hash != self._tip_hash:
            raise EventLogCorrupt("event prev_hash does not match current log tip")
        line = json.dumps(
            finalized.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8") + b"\n"
        with self.path.open("ab") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
        self._tip_hash, self._count = finalized.event_hash, self._count + 1
        return finalized

    def append_new(
        self,
        *,
        event_id: str,
        event_type: str,
        payload: dict[str, Any],
        actor: str = "system",
        schema_version: str = SCHEMA_VERSION,
    ) -> ProjectEvent:
        return self.append(ProjectEvent(
            event_id, event_type, payload, schema_version,
            actor=actor, prev_hash=self._tip_hash,
        ))

    def iter_events(self) -> Iterator[ProjectEvent]:
        if not self.path.exists():
            return
        previous: str | None = None
        with self.path.open("rb") as handle:
            for line_number, raw in enumerate(handle, start=1):
                if not raw.strip():
                    continue
                try:
                    data = json.loads(raw)
                    event = ProjectEvent(
                        event_id=data["event_id"],
                        event_type=data["event_type"],
                        payload=data["payload"],
                        schema_version=data.get("schema_version", "0.2"),
                        created_at=data["created_at"],
                        actor=data.get("actor", "system"),
                        prev_hash=data.get("prev_hash"),
                        event_hash=data.get("event_hash"),
                    )
                except (KeyError, TypeError, json.JSONDecodeError) as exc:
                    raise EventLogCorrupt(f"line {line_number}: malformed event") from exc
                if event.event_hash is None or event.event_hash != event.computed_hash():
                    raise EventLogCorrupt(f"line {line_number}: event hash mismatch")
                if event.prev_hash != previous:
                    raise EventLogCorrupt(f"line {line_number}: hash-chain break")
                previous = event.event_hash
                yield event

    def read_all(self) -> list[dict[str, Any]]:
        return [event.to_dict() for event in self.iter_events()]

    @property
    def tip_hash(self) -> str | None:
        return self._tip_hash

    @property
    def count(self) -> int:
        return self._count


class SnapshotStore:
    """Atomic snapshots. The filename is the snapshot content hash."""

    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def write(self, payload: dict[str, Any], *, name: str = "snapshot") -> ContentHash:
        canonical = json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
        ).encode("utf-8")
        digest = hash_bytes(canonical)
        target = self.directory / f"{digest.hex}.json"
        if target.exists():
            return digest
        temp = self.directory / f".{name}.{os.getpid()}.tmp"
        with temp.open("wb") as handle:
            handle.write(canonical)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, target)
        dir_fd = os.open(self.directory, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
        return digest

    def read(self, digest: ContentHash) -> dict[str, Any]:
        target = self.directory / f"{digest.hex}.json"
        raw = target.read_bytes()
        if hash_bytes(raw) != digest:
            raise EventLogCorrupt(f"snapshot hash mismatch: {digest}")
        return json.loads(raw)
