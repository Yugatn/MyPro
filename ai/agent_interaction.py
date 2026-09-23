"""Deterministic state machine for Mira/Grok interaction.

The module contains no LLM calls and no side effects. It converts verified
protocol facts into the next allowed interaction state.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class InteractionState(str, Enum):
    RECEIVED = "received"
    CONTEXT_LOADING = "context_loading"
    READY_FOR_ASSIGNMENT = "ready_for_assignment"
    ASSIGNED = "assigned"
    RUNNING = "running"
    RESULT_PENDING_VERIFICATION = "result_pending_verification"
    VERIFIED = "verified"
    CONFLICT = "conflict"
    PROPOSAL_READY = "proposal_ready"
    DECISION_REQUIRED = "decision_required"
    ACTION_READY = "action_ready"
    COMPLETED = "completed"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class AgentResult:
    agent_id: str
    status: str
    has_evidence: bool
    verification_state: str
    has_conflict: bool = False


@dataclass(frozen=True)
class InteractionDecision:
    state: InteractionState
    reason: str


def next_state(
    *,
    current: InteractionState,
    results: Iterable[AgentResult] = (),
    requires_human_decision: bool = False,
    action_authorized: bool = False,
    action_executed: bool = False,
) -> InteractionDecision:
    """Return the next protocol state without performing side effects."""

    results = tuple(results)

    if current is InteractionState.RECEIVED:
        return InteractionDecision(
            InteractionState.CONTEXT_LOADING,
            "load canonical project context before assignment",
        )

    if current is InteractionState.CONTEXT_LOADING:
        return InteractionDecision(
            InteractionState.READY_FOR_ASSIGNMENT,
            "context loaded; task may be decomposed and assigned",
        )

    if current is InteractionState.READY_FOR_ASSIGNMENT:
        return InteractionDecision(
            InteractionState.ASSIGNED,
            "assignment created with stable task and idempotency identifiers",
        )

    if current is InteractionState.ASSIGNED:
        return InteractionDecision(
            InteractionState.RUNNING,
            "assigned agent may execute within declared capabilities",
        )

    if current is InteractionState.RUNNING:
        if not results:
            return InteractionDecision(
                InteractionState.RUNNING,
                "await result envelope",
            )
        if any(r.has_conflict for r in results):
            return InteractionDecision(
                InteractionState.CONFLICT,
                "incompatible observations require independent verification",
            )
        if any(r.verification_state == "verified" for r in results):
            return InteractionDecision(
                InteractionState.VERIFIED,
                "at least one result has independent verification",
            )
        return InteractionDecision(
            InteractionState.RESULT_PENDING_VERIFICATION,
            "result received but independent verification is incomplete",
        )

    if current is InteractionState.RESULT_PENDING_VERIFICATION:
        if any(r.has_conflict for r in results):
            return InteractionDecision(
                InteractionState.CONFLICT,
                "verification detected or preserved a conflict",
            )
        if all(r.verification_state == "verified" for r in results):
            return InteractionDecision(
                InteractionState.VERIFIED,
                "required results independently verified",
            )
        return InteractionDecision(
            InteractionState.RESULT_PENDING_VERIFICATION,
            "retain evidence and request verification",
        )

    if current is InteractionState.CONFLICT:
        return InteractionDecision(
            InteractionState.DECISION_REQUIRED if requires_human_decision
            else InteractionState.RESULT_PENDING_VERIFICATION,
            "conflict cannot be silently resolved",
        )

    if current is InteractionState.VERIFIED:
        return InteractionDecision(
            InteractionState.PROPOSAL_READY,
            "verified evidence may be converted into a project proposal",
        )

    if current is InteractionState.PROPOSAL_READY:
        return InteractionDecision(
            InteractionState.DECISION_REQUIRED,
            "proposal requires the configured policy/decision gate",
        )

    if current is InteractionState.DECISION_REQUIRED:
        if not action_authorized:
            return InteractionDecision(
                InteractionState.DECISION_REQUIRED,
                "wait for explicit authorization",
            )
        return InteractionDecision(
            InteractionState.ACTION_READY,
            "authorization is present; action may be dispatched",
        )

    if current is InteractionState.ACTION_READY:
        if not action_executed:
            return InteractionDecision(
                InteractionState.ACTION_READY,
                "authorized action has not executed yet",
            )
        return InteractionDecision(
            InteractionState.COMPLETED,
            "action executed; persist revision and evidence",
        )

    return InteractionDecision(
        InteractionState.BLOCKED,
        "terminal or unsupported state requires explicit orchestration",
    )
