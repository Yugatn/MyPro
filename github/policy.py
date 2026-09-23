from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

class AuthorizationError(PermissionError):
    pass

@dataclass(frozen=True)
class GitHubAuthorization:
    authorization_id: str
    task_id: str
    repository: str
    actor: str
    allowed_operations: frozenset[str]
    allowed_paths: tuple[str, ...] = ()
    target_branch: str = "main"

    def permits(self, operation: str, *, repository: str, path: str | None = None) -> bool:
        if repository != self.repository or operation not in self.allowed_operations:
            return False
        if path is not None and self.allowed_paths:
            return any(path == p or path.startswith(p.rstrip("/") + "/") for p in self.allowed_paths)
        return True

def validate_authorization(auth: GitHubAuthorization, *, repository: str,
                           operation: str, paths: Iterable[str] = ()) -> None:
    if not auth.authorization_id or not auth.task_id or not auth.actor:
        raise AuthorizationError("authorization identity is incomplete")
    if not auth.permits(operation, repository=repository):
        raise AuthorizationError("authorization does not permit " + operation)
    for path in paths:
        if not auth.permits(operation, repository=repository, path=path):
            raise AuthorizationError("authorization does not permit path " + path)
