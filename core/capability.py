"""Scoped, expiring, revocable capability security."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable

from .errors import CapabilityDenied
from .identity import new_id


class Operation:
    MEDIA_READ = "media.read"
    MEDIA_METADATA_READ = "media.metadata.read"
    ANALYSIS_WRITE = "analysis.write"
    PROJECT_READ = "project.read"
    PROJECT_WRITE = "project.write"
    NETWORK_ACCESS = "network.access"
    STORAGE_READ = "storage.read"
    STORAGE_WRITE = "storage.write"
    UI_ACCESS = "ui.access"
    EVENT_SUBSCRIBE = "event.subscribe"


def scope_matches(pattern: str, resource: str) -> bool:
    if pattern == "*":
        return True
    p_parts, r_parts = pattern.split(":"), resource.split(":")
    if len(p_parts) > len(r_parts):
        return False
    return all(p == "*" or p == r for p, r in zip(p_parts, r_parts)) and len(p_parts) == len(r_parts)


def scope_covers(parent: str, child: str) -> bool:
    if parent == "*":
        return True
    if child == "*":
        return False
    p_parts, c_parts = parent.split(":"), child.split(":")
    if len(p_parts) > len(c_parts):
        return False
    return all(p == "*" or p == c for p, c in zip(p_parts, c_parts))


@dataclass(frozen=True, slots=True)
class Capability:
    id: str
    subject: str
    operations: frozenset[str]
    resource_scope: str
    issued_at: datetime
    expires_at: datetime
    delegable: bool
    revocable: bool = True
    parent: str | None = None


class CapabilityIssuer:
    def __init__(self) -> None:
        self._issued: dict[str, Capability] = {}
        self._revoked: set[str] = set()

    def issue(self, *, subject: str, operations: Iterable[str], resource_scope: str,
              ttl_seconds: int, delegable: bool = False, parent: str | None = None) -> Capability:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        ops = frozenset(operations)
        now = datetime.now(timezone.utc)
        parent_cap = self._issued.get(parent) if parent else None
        if parent:
            if parent_cap is None or parent in self._revoked:
                raise CapabilityDenied("parent capability unavailable")
            if not parent_cap.delegable or not ops.issubset(parent_cap.operations):
                raise CapabilityDenied("delegation would amplify operations")
            if not scope_covers(parent_cap.resource_scope, resource_scope):
                raise CapabilityDenied("delegation would amplify scope")
            if now >= parent_cap.expires_at:
                raise CapabilityDenied("parent capability expired")
            expires_at = min(now + timedelta(seconds=ttl_seconds), parent_cap.expires_at)
        else:
            expires_at = now + timedelta(seconds=ttl_seconds)

        cap = Capability(
            id=new_id("cap"), subject=subject, operations=ops,
            resource_scope=resource_scope, issued_at=now, expires_at=expires_at,
            delegable=delegable, parent=parent,
        )
        self._issued[cap.id] = cap
        return cap

    def revoke(self, cap_id: str) -> None:
        if cap_id not in self._issued:
            raise CapabilityDenied("unknown capability")
        self._revoked.add(cap_id)

    def check(self, cap_id: str, operation: str, resource: str | None = None) -> None:
        if cap_id in self._revoked:
            raise CapabilityDenied("capability revoked")
        cap = self._issued.get(cap_id)
        if cap is None:
            raise CapabilityDenied("unknown capability")
        if datetime.now(timezone.utc) >= cap.expires_at:
            raise CapabilityDenied("capability expired")
        if operation not in cap.operations:
            raise CapabilityDenied(f"operation denied: {operation}")
        if resource is not None and not scope_matches(cap.resource_scope, resource):
            raise CapabilityDenied(f"resource denied: {resource}")
