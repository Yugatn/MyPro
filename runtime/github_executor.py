from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from github.gateway import FineGrainedPATGateway, GitHubChange
from github.policy import GitHubAuthorization, AuthorizationError
from protocol.events import EventEnvelope, EventType
from protocol.state_machine import ProtocolState
from runtime.orchestrator import AgentProtocolRuntime


class GitHubExecutionError(RuntimeError):
    pass


@dataclass(frozen=True)
class GitHubExecutionResult:
    task_id: str
    authorization_id: str
    repository: str
    branch: str
    target_branch: str
    pull_request: Mapping[str, object]
    commits: tuple[Mapping[str, object], ...]


class AuthorizedGitHubExecutor:
    """Binds ACTION_READY runtime state to a scoped GitHub authorization."""

    def execute(
        self,
        *,
        runtime: AgentProtocolRuntime,
        authorization: GitHubAuthorization,
        authorization_event: EventEnvelope,
        branch: str,
        base_sha: str,
        changes: Iterable[GitHubChange],
        pr_title: str,
        pr_body: str,
        gateway: FineGrainedPATGateway,
    ) -> GitHubExecutionResult:
        if authorization_event.event_type is not EventType.ACTION_AUTHORIZED:
            raise GitHubExecutionError("execution requires ACTION_AUTHORIZED event")
        if authorization_event.task_id != authorization.task_id:
            raise GitHubExecutionError("authorization task does not match event task")
        if runtime.state.get(authorization.task_id) is not ProtocolState.ACTION_READY:
            raise GitHubExecutionError("task is not ACTION_READY")
        payload = authorization_event.payload
        if payload.get("authorization_id") != authorization.authorization_id:
            raise GitHubExecutionError("authorization id mismatch")
        if payload.get("repository") != authorization.repository:
            raise GitHubExecutionError("authorization repository mismatch")

        changes = tuple(changes)
        if not changes:
            raise GitHubExecutionError("at least one GitHub change is required")
        if "write_branch" not in authorization.allowed_operations:
            raise AuthorizationError("authorization does not permit write_branch")
        if "create_pr" not in authorization.allowed_operations:
            raise AuthorizationError("authorization does not permit create_pr")

        result = gateway.apply_authorized_change(
            authorization=authorization,
            branch=branch,
            base_sha=base_sha,
            changes=list(changes),
            pr_title=pr_title,
            pr_body=pr_body,
        )

        change_event = runtime.make_event(
            event_type=EventType.GITHUB_CHANGE,
            task_id=authorization.task_id,
            issuer=authorization_event.issuer,
            correlation_id=authorization_event.correlation_id,
            payload={
                "authorized": True,
                "authorization_id": authorization.authorization_id,
                "repository": authorization.repository,
                "operation": "write_branch",
                "branch": branch,
                "target_branch": authorization.target_branch,
                "pull_request_number": result["pull_request"].get("number"),
            },
            evidence_refs=(
                {"type": "github_pr", "value": result["pull_request"].get("html_url")},
            ),
        )
        runtime.ingest(change_event)

        revision_event = runtime.make_event(
            event_type=EventType.REVISION_RECORDED,
            task_id=authorization.task_id,
            issuer=authorization_event.issuer,
            correlation_id=authorization_event.correlation_id,
            payload={
                "status": "executed",
                "authorization_id": authorization.authorization_id,
                "repository": authorization.repository,
                "branch": branch,
                "pull_request": result["pull_request"],
                "commit_count": len(result["commits"]),
            },
            evidence_refs=(
                {"type": "github_pr", "value": result["pull_request"].get("html_url")},
            ),
        )
        runtime.ingest(revision_event)

        return GitHubExecutionResult(
            task_id=authorization.task_id,
            authorization_id=authorization.authorization_id,
            repository=authorization.repository,
            branch=branch,
            target_branch=authorization.target_branch,
            pull_request=result["pull_request"],
            commits=tuple(result["commits"]),
        )
