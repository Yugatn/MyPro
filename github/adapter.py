from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Any

class GitHubGateway(Protocol):
    def read_file(self, path: str, ref: str = "main") -> str: ...
    def read_commit(self, sha: str) -> dict[str, Any]: ...
    def apply_authorized_change(self, *, authorization_id: str, changes: list[dict[str, Any]]) -> dict[str, Any]: ...

@dataclass(frozen=True)
class GitHubEvidence:
    kind: str
    repository: str
    ref: str
    value: str
    content_hash: str | None = None

class UnauthorizedGitHubGateway:
    """Safe default: reads may be supplied by an integration; writes are denied."""
    def read_file(self, path: str, ref: str = "main") -> str:
        raise NotImplementedError("connect a GitHubGateway implementation")
    def read_commit(self, sha: str) -> dict[str, Any]:
        raise NotImplementedError("connect a GitHubGateway implementation")
    def apply_authorized_change(self, *, authorization_id: str, changes: list[dict[str, Any]]) -> dict[str, Any]:
        raise PermissionError("GitHub writes require an authorized gateway")
