"""Mira adapter for MyPro agent orchestration.

This adapter is deliberately provider-neutral. It consumes agent result
envelopes, reconciles Grok work, creates deterministic child tasks and emits
MyPro-style proposals. It never performs project mutations itself.
"""

from __future__ import annotations

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
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return f"{prefix}_{sha256(canonical.encode('utf-8')).hexdigest()[:16]}"


class MiraAdapter:
    """Deterministic orchestration boundary for Mira.

    The adapter can be connected to an LLM provider later. The provider is
    expected to produce proposals; this layer remains responsible for
    provenance, reconciliation and authority boundaries.
    """

    def consume_grok_results(
        self,
        task: MiraTask,
        results: Iterable[MiraResult],
    ) -> dict[str, Any]:
        results = tuple(results)
        grok = tuple(r for r in results if r.agent_id.lower() == "grok")

        if not grok:
            return {
                "status": "missing",
                "task_id": task.task_id,
                "next_action": "request_grok_result",
            }

        conflicts = self._find_conflicts(grok)
        if conflicts:
            return {
                "status": "conflict",
                "task_id": task.task_id,
                "result_ids": tuple(r.result_id for r in grok),
                "conflicts": conflicts,
                "next_action": "independent_verification",
            }

        verified = tuple(r for r in grok if r.verification_state == "verified")
        unverified = tuple(r for r in grok if r.verification_state != "verified")

        return {
            "status": "verified" if verified else "pending_verification",
            "task_id": task.task_id,
            "verified_result_ids": tuple(r.result_id for r in verified),
            "unverified_result_ids": tuple(r.result_id for r in unverified),
            "evidence": tuple(e for r in grok for e in r.evidence),
            "artifacts": tuple(a for r in grok for a in r.artifacts),
            "next_action": (
                "create_proposal" if verified else "request_independent_verification"
            ),
        }

    def create_remaining_work_task(
        self,
        parent: MiraTask,
        *,
        remaining_objective: str,
        assigned_agent: str,
    ) -> MiraTask:
        payload = {
            "parent_task_id": parent.task_id,
            "objective": remaining_objective,
            "assigned_agent": assigned_agent,
            "correlation_id": parent.correlation_id,
        }
        child_id = stable_id("task", payload)
        return MiraTask(
            task_id=child_id,
            objective=remaining_objective,
            parent_task_id=parent.task_id,
            correlation_id=parent.correlation_id,
            idempotency_key=stable_id("idem", payload),
        )

    def create_proposal(
        self,
        task: MiraTask,
        results: Iterable[MiraResult],
        *,
        changes: Iterable[Mapping[str, Any]],
        intent: str,
        policy_context: Mapping[str, Any] | None = None,
    ) -> MiraProposal:
        results = tuple(results)
        verified = tuple(r for r in results if r.verification_state == "verified")

        if not verified:
            raise ValueError("Proposal requires at least one independently verified result")

        evidence = tuple(e for r in verified for e in r.evidence)
        payload = {
            "task_id": task.task_id,
            "result_ids": [r.result_id for r in verified],
            "changes": list(changes),
            "intent": intent,
        }
        return MiraProposal(
            proposal_id=stable_id("proposal", payload),
            task_id=task.task_id,
            title=f"Mira proposal for {task.task_id}",
            intent=intent,
            source_result_ids=tuple(r.result_id for r in verified),
            evidence_refs=evidence,
            changes=tuple(changes),
            verification_state="verified",
            requires_decision=True,
            policy_context=policy_context or {},
        )

    @staticmethod
    def _find_conflicts(results: tuple[MiraResult, ...]) -> tuple[dict[str, Any], ...]:
        observed: dict[str, tuple[str, str]] = {}
        conflicts: list[dict[str, Any]] = []

        for result in results:
            for claim in result.claims:
                if claim.get("category") != "OBSERVED":
                    continue
                statement = str(claim.get("statement", ""))
                key, _, value = statement.partition("=")
                if not key:
                    continue
                prior = observed.get(key)
                if prior and prior[1] != value:
                    conflicts.append({
                        "key": key,
                        "first_result_id": prior[0],
                        "second_result_id": result.result_id,
                        "first_value": prior[1],
                        "second_value": value,
                    })
                else:
                    observed[key] = (result.result_id, value)

        return tuple(conflicts)
