"""Provider-neutral Mira orchestration adapter."""
from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Any, Iterable, Mapping

@dataclass(frozen=True)
class MiraTask:
    task_id: str
    objective: str
    parent_task_id: str | None = None
    correlation_id: str = ""
    idempotency_key: str = ""

@dataclass(frozen=True)
class MiraResult:
    result_id: str
    task_id: str
    agent_id: str
    status: str
    summary: str
    artifacts: tuple[Mapping[str, Any], ...] = ()
    evidence: tuple[Mapping[str, Any], ...] = ()
    claims: tuple[Mapping[str, Any], ...] = ()
    tests_performed: tuple[str, ...] = ()
    verification_state: str = "unverified"
    uncertainty: str | None = None
    requested_next_action: str | None = None

@dataclass(frozen=True)
class MiraProposal:
    proposal_id: str
    task_id: str
    title: str
    intent: str
    source_result_ids: tuple[str, ...]
    evidence_refs: tuple[Mapping[str, Any], ...]
    changes: tuple[Mapping[str, Any], ...]
    verification_state: str
    requires_decision: bool = True
    policy_context: Mapping[str, Any] = field(default_factory=dict)

def stable_id(prefix: str, payload: Mapping[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return f"{prefix}_{sha256(raw.encode()).hexdigest()[:16]}"

class MiraAdapter:
    def consume_grok_results(self, task: MiraTask, results: Iterable[MiraResult]) -> dict[str, Any]:
        results = tuple(r for r in results if r.agent_id.lower() == "grok")
        if not results:
            return {"status": "missing", "task_id": task.task_id, "next_action": "request_grok_result"}
        conflicts = self._find_conflicts(results)
        if conflicts:
            return {"status": "conflict", "task_id": task.task_id,
                    "result_ids": tuple(r.result_id for r in results),
                    "conflicts": conflicts, "next_action": "independent_verification"}
        verified = tuple(r for r in results if r.verification_state == "verified")
        return {"status": "verified" if verified else "pending_verification",
                "task_id": task.task_id,
                "verified_result_ids": tuple(r.result_id for r in verified),
                "unverified_result_ids": tuple(r.result_id for r in results if r not in verified),
                "evidence": tuple(e for r in results for e in r.evidence),
                "artifacts": tuple(a for r in results for a in r.artifacts),
                "next_action": "create_proposal" if verified else "request_independent_verification"}

    def create_remaining_work_task(self, parent: MiraTask, *, remaining_objective: str,
                                    assigned_agent: str) -> MiraTask:
        payload = {"parent_task_id": parent.task_id, "objective": remaining_objective,
                   "assigned_agent": assigned_agent, "correlation_id": parent.correlation_id}
        return MiraTask(stable_id("task", payload), remaining_objective, parent.task_id,
                        parent.correlation_id, stable_id("idem", payload))

    def create_proposal(self, task: MiraTask, results: Iterable[MiraResult], *,
                        changes: Iterable[Mapping[str, Any]], intent: str,
                        policy_context: Mapping[str, Any] | None = None) -> MiraProposal:
        verified = tuple(r for r in results if r.verification_state == "verified")
        if not verified:
            raise ValueError("Proposal requires independently verified result")
        changes = tuple(changes)
        payload = {"task_id": task.task_id, "result_ids": [r.result_id for r in verified],
                   "changes": list(changes), "intent": intent}
        return MiraProposal(stable_id("proposal", payload), task.task_id,
                            f"Mira proposal for {task.task_id}", intent,
                            tuple(r.result_id for r in verified),
                            tuple(e for r in verified for e in r.evidence),
                            changes, "verified", True, policy_context or {})

    @staticmethod
    def _find_conflicts(results: tuple[MiraResult, ...]) -> tuple[dict[str, Any], ...]:
        observed, conflicts = {}, []
        for result in results:
            for claim in result.claims:
                if claim.get("category") != "OBSERVED": continue
                key, _, value = str(claim.get("statement", "")).partition("=")
                if not key: continue
                if key in observed and observed[key][1] != value:
                    conflicts.append({"key": key, "first_result_id": observed[key][0],
                                      "second_result_id": result.result_id,
                                      "first_value": observed[key][1], "second_value": value})
                else: observed[key] = (result.result_id, value)
        return tuple(conflicts)
