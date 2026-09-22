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

    def to_dict(self):
        return {"event_id":self.event_id,"event_type":self.event_type,"payload":self.payload,
                "prev_hash":str(self.prev_hash) if self.prev_hash else None,
                "event_hash":str(self.event_hash),"schema_version":self.schema_version,
                "created_at":self.created_at}


class EventLog:
    def __init__(self,path:str|Path):
        self.path=Path(path); self._tip=None; self._count=0
        if self.path.exists(): self.recover_tail()

    @property
    def tip_hash(self): return self._tip

    @property
    def count(self): return self._count

    @staticmethod
    def _event_hash(event_id,event_type,payload,prev_hash,schema_version,created_at):
        return hash_canonical({"event_id":event_id,"event_type":event_type,"payload":payload,
            "prev_hash":str(prev_hash) if prev_hash else None,
            "schema_version":schema_version,"created_at":created_at})

    def append(self,*,type,payload,actor="system",event_id=None):
        import uuid
        event_id=event_id or f"evt_{uuid.uuid4().hex}"
        created_at=datetime.now(timezone.utc).isoformat()
        body=dict(payload); body.setdefault("_actor",actor)
        digest=self._event_hash(event_id,type,body,self._tip,"0.4",created_at)
        event=ProjectEvent(event_id,type,body,self._tip,digest,created_at=created_at)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        raw=(json.dumps(event.to_dict(),ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n").encode()
        with self.path.open("ab") as h:
            h.write(raw); h.flush(); os.fsync(h.fileno())
        self._tip,self._count=digest,self._count+1
        return event

    def read_all(self):
        return list(self.iter_events())

    def recover_tail(self):
        if not self.path.exists(): return
        data=self.path.read_bytes()
        lines=data.splitlines(keepends=True)
        good=[]; tail_corrupt=False
        for i,line in enumerate(lines):
            if not line.strip(): continue
            try: json.loads(line)
            except (UnicodeDecodeError,json.JSONDecodeError):
                if i==len(lines)-1 and not data.endswith((b"\n",b"\r")):
                    tail_corrupt=True; break
                raise EventLogCorrupt("corrupt event line")
            good.append(line)
        if tail_corrupt:
            self.path.write_bytes(b"".join(good))
        list(self.iter_events())

    def iter_events(self):
        if not self.path.exists():
            self._tip,self._count=None,0; return
        previous=None; count=0
        with self.path.open("rb") as h:
            for raw in h:
                if not raw.strip(): continue
                try: data=json.loads(raw)
                except (UnicodeDecodeError,json.JSONDecodeError) as exc:
                    raise EventLogCorrupt("corrupt event line") from exc
                if data.get("prev_hash")!=(str(previous) if previous else None):
                    raise EventLogCorrupt("event chain break")
                expected=self._event_hash(data["event_id"],data["event_type"],data["payload"],
                    previous,data["schema_version"],data["created_at"])
                if data.get("event_hash")!=str(expected):
                    raise EventLogCorrupt("event hash mismatch")
                previous=expected; count+=1; yield data
        self._tip,self._count=previous,count


class SnapshotStore:
    def __init__(self,directory:str|Path):
        self.directory=Path(directory); self.directory.mkdir(parents=True,exist_ok=True)

    def write(self,*,name,payload):
        digest=hash_canonical(payload)
        target=self.directory/f"{digest.hex}.json"; tmp=target.with_suffix(".tmp")
        raw=json.dumps(payload,ensure_ascii=False,sort_keys=True,indent=2).encode()
        with tmp.open("wb") as h:
            h.write(raw); h.flush(); os.fsync(h.fileno())
        os.replace(tmp,target)
        return digest

    def read(self,digest):
        target=self.directory/f"{digest.hex}.json"
        if not target.exists(): raise FileNotFoundError(target)
        payload=json.loads(target.read_text(encoding="utf-8"))
        if hash_canonical(payload)!=digest: raise EventLogCorrupt("snapshot hash mismatch")
        return payload
