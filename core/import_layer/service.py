"""Import proposal boundary.

Adapters only produce immutable evidence. This service records proposals,
decisions and applied revisions in the project event log.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from ..identity import new_id
from ..policy import DecisionKind, PolicyEngine
from ..project import Project
from .base import ImportResult
from .otio_adapter import OTIOAdapter

MergeStrategy = Literal["replace", "merge", "append"]


@dataclass(frozen=True, slots=True)
class ImportProposal:
    id: str
    result_id: str
    source_hash: str
    merge_strategy: MergeStrategy
    reversible: bool = True

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "result_id": self.result_id,
            "source_hash": self.source_hash,
            "merge_strategy": self.merge_strategy,
            "reversible": self.reversible,
        }


class ImportService:
    def __init__(self, adapter: OTIOAdapter | None = None) -> None:
        self.adapter = adapter or OTIOAdapter()

    def dry_run(self, path: Path) -> ImportResult:
        if path.suffix.lower() not in self.adapter.supported_extensions:
            raise ValueError(f"unsupported extension: {path.suffix}")
        return self.adapter.import_project(path)

    def propose(
        self,
        project: Project,
        result: ImportResult,
        *,
        merge_strategy: MergeStrategy = "replace",
        policy: PolicyEngine | None = None,
    ) -> ImportProposal:
        proposal = ImportProposal(
            id=new_id("proposal"),
            result_id=result.id,
            source_hash=result.manifest.source.source_hash,
            merge_strategy=merge_strategy,
        )
        engine = policy or PolicyEngine()
        risk = "critical" if result.manifest.losses.has_critical() else "low"
        decision, reason = engine.evaluate({
            "proposal.action": "import_project",
            "proposal.risk": risk,
            "proposal.reversible": proposal.reversible,
        })
        project.append_event(
            "proposal.import_project",
            {
                "proposal": proposal.as_dict(),
                "result": result.as_dict(),
                "policy": {"decision": decision.value, "reason": reason},
            },
            actor=f"adapter:{result.adapter_id}@{result.adapter_version}",
        )
        return proposal

    def decide(self, project: Project, proposal: ImportProposal, *, approved: bool, actor: str = "human") -> None:
        project.append_event(
            "decision.recorded",
            {"proposal_id": proposal.id, "approved": approved},
            actor=actor,
        )

    def apply(self, project: Project, proposal: ImportProposal, result: ImportResult, *, approved: bool) -> str:
        if result.id != proposal.result_id:
            raise ValueError("proposal/result mismatch")
        if result.manifest.source.source_hash != proposal.source_hash:
            raise ValueError("proposal/source hash mismatch")
        if not approved:
            raise PermissionError("import proposal was not approved")
        decisions = [
            event for event in project.log.iter_events()
            if event.event_type == "decision.recorded"
            and event.payload.get("proposal_id") == proposal.id
        ]
        if not decisions or decisions[-1].payload.get("approved") is not True:
            raise PermissionError("no recorded approval for import proposal")
        revision_id = new_id("revision")
        project.snapshot({"revision_id": revision_id, "candidate": result.canonical_candidate})
        project.append_event(
            "action.import_project",
            {"proposal_id": proposal.id, "result_id": result.id, "revision_id": revision_id},
            actor="system",
        )
        project.append_event(
            "revision.created",
            {
                "revision_id": revision_id,
                "proposal_id": proposal.id,
                "merge_strategy": proposal.merge_strategy,
                "reversible": proposal.reversible,
            },
            actor="system",
        )
        return revision_id
