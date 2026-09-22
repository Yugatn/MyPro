"""Explicit policy boundary for proposals."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class DecisionKind(str, Enum):
    ALLOW = "allow"
    REVIEW = "review"
    DENY = "deny"


@dataclass(frozen=True)
class Policy:
    auto_apply_reversible: bool = False
    deny_critical_loss: bool = False


DEFAULT_POLICY = Policy()


class PolicyEngine:
    def __init__(self, policy: Policy = DEFAULT_POLICY) -> None:
        self.policy = policy

    def evaluate(self, proposal: dict[str, Any]) -> tuple[DecisionKind, str]:
        if proposal.get("proposal.risk") == "critical" and self.policy.deny_critical_loss:
            return DecisionKind.DENY, "critical loss is denied by policy"
        if self.policy.auto_apply_reversible and proposal.get("proposal.reversible", False):
            return DecisionKind.ALLOW, "explicit reversible auto-apply policy"
        return DecisionKind.REVIEW, "explicit decision is required"
