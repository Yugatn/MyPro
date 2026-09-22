"""Append-only hash-chained event log and atomic snapshots."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any

from core.identity import ContentHash, hash_canonical


class EventLogCorrupt(RuntimeError):
    pass


@dataclass(frozen=True)
class ProjectEvent:
    event_id: str
    event_type: str
    payload: dict[str, Any]
    prev_hash: ContentHash | None
    event_hash: ContentHash
    schema_version: str = "0.4"
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "payload": self.payload,
            "prev_hash": str(self.prev_hash) if self.prev_hash else None,
            "event_hash": str(self.event_hash),
            "schema_version": self.schema_version,
            "created_at": self.created_at,
        }


class EventLog:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._tip: ContentHash | None = None
        self._count = 0
        if self.path.exists():
            list(self.iter_events())

    @property
    def tip_hash(self) -> ContentHash | None:
        return self._tip

    @property
    def count(self) -> int:
        return self._count

    def _event_hash(self, event_id: str, event_type: str, payload: dict[str, Any],
                    prev_hash: ContentHash | None, schema_version: str, created_at: str) -> ContentHash:
        return hash_canonical({
            "event_id": event_id, "event_type": event_type, "payload": payload,
            "prev_hash": str(prev_hash) if prev_hash else None,
            "schema_version": schema_version, "created_at": created_at,
        })

    def append(self, *, type: str, payload: dict[str, Any], actor: str = "system",
               event_id: str | None = None) -> ProjectEvent:
        import uuid
        event_id = event_id or f"evt_{uuid.uuid4().hex}"
        created_at = datetime.now(timezone.utc).isoformat()
        body = dict(payload)
        body.setdefault("_actor", actor)
        event_hash = self._event_hash(event_id, type, body, self._tip, "0.4", created_at)
        event = ProjectEvent(event_id, type, body, self._tip, event_hash, created_at=created_at)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(event.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        with self.path.open("ab") as handle:
            handle.write((line + "\n").encode("utf-8"))
            handle.flush()
            os.fsync(handle.fileno())
        self._tip, self._count = event.event_hash, self._count + 1
        return event

    def iter_events(self):
        if not self.path.exists():
            self._tip, self._count = None, 0
            return
        valid: list[bytes] = []
        with self.path.open("rb") as handle:
            for raw in handle:
                if not raw.strip():
                    continue
                try:
                    json.loads(raw)
                except (UnicodeDecodeError, json.JSONDecodeError):
                    # Only an incomplete final line is recoverable.
                    if handle.peek(1) if hasattr(handle, "peek") else False:
                        raise EventLogCorrupt("corrupt event line")
                    break
                valid.append(raw)
        if valid and not self.path.read_bytes().endswith(valid[-1]):
            raise EventLogCorrupt("invalid event log tail")
        previous: ContentHash | None = None
        count = 0
        for raw in valid:
            data = json.loads(raw)
            expected_prev = data.get("prev_hash")
            if expected_prev != (str(previous) if previous else None):
                raise EventLogCorrupt("event chain break")
            expected = self._event_hash(
                data["event_id"], data["event_type"], data["payload"],
                previous, data["schema_version"], data["created_at"],
            )
            if data.get("event_hash") != str(expected):
                raise EventLogCorrupt("event hash mismatch")
            previous = expected
            count += 1
            yield data
        self._tip, self._count = previous, count

    def recover_tail(self) -> None:
        if not self.path.exists():
            return
        data = self.path.read_bytes()
        lines = data.splitlines(keepends=True)
        good = []
        for line in lines:
            try:
                json.loads(line)
                good.append(line)
            except (UnicodeDecodeError, json.JSONDecodeError):
                break
        self.path.write_bytes(b"".join(good))
        list(self.iter_events())


class SnapshotStore:
    def __init__(self, directory: str | Path):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def write(self, *, name: str, payload: dict[str, Any]) -> ContentHash:
        digest = hash_canonical(payload)
        target = self.directory / f"{digest.hex}.json"
        tmp = target.with_suffix(".tmp")
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8")
        with tmp.open("wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, target)
        return digest

    def read(self, digest: ContentHash) -> dict[str, Any]:
        target = self.directory / f"{digest.hex}.json"
        if not target.exists():
            raise FileNotFoundError(target)
        payload = json.loads(target.read_text(encoding="utf-8"))
        if hash_canonical(payload) != digest:
            raise EventLogCorrupt("snapshot hash mismatch")
        return payload
