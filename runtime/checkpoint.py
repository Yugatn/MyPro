from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class ExecutionCheckpoint:
    """Durable resume point for bounded agent execution."""

    task_id: str
    phase: str
    last_completed_step: str
    next_step: str
    known_facts: tuple[str, ...] = ()
    evidence_refs: tuple[Mapping[str, Any], ...] = ()
    completed_calls: tuple[str, ...] = ()
    files_changed: tuple[str, ...] = ()
    tests_status: str = "unknown"
    ci_status: str = "unknown"
    attempt: int = 1

    def __post_init__(self) -> None:
        if not self.task_id or not self.phase or not self.next_step:
            raise ValueError("checkpoint identity and next_step are required")
        if self.attempt < 1:
            raise ValueError("attempt must be >= 1")

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def json(self) -> str:
        return json.dumps(self.as_dict(), sort_keys=True, ensure_ascii=False, indent=2)


class CheckpointStore:
    """Small durable JSON store; writes atomically and never executes work."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def save(self, checkpoint: ExecutionCheckpoint) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(checkpoint.json() + "\n", encoding="utf-8")
        tmp.replace(self.path)

    def load(self) -> ExecutionCheckpoint | None:
        if not self.path.exists():
            return None
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return ExecutionCheckpoint(
            task_id=data["task_id"],
            phase=data["phase"],
            last_completed_step=data["last_completed_step"],
            next_step=data["next_step"],
            known_facts=tuple(data.get("known_facts", ())),
            evidence_refs=tuple(data.get("evidence_refs", ())),
            completed_calls=tuple(data.get("completed_calls", ())),
            files_changed=tuple(data.get("files_changed", ())),
            tests_status=data.get("tests_status", "unknown"),
            ci_status=data.get("ci_status", "unknown"),
            attempt=int(data.get("attempt", 1)),
        )


class BoundedExecutionPolicy:
    """Limits one execution tranche without limiting the whole task."""

    def __init__(self, max_calls_per_tranche: int = 3):
        if max_calls_per_tranche < 1:
            raise ValueError("max_calls_per_tranche must be >= 1")
        self.max_calls_per_tranche = max_calls_per_tranche

    def select_next(self, *, completed_calls: set[str], candidates: list[str]) -> str | None:
        for candidate in candidates:
            if candidate not in completed_calls:
                return candidate
        return None
