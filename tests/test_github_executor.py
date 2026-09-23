import pytest

from github.gateway import GitHubChange
from github.policy import GitHubAuthorization
from protocol.events import EventType
from protocol.state_machine import ProtocolState
from runtime.github_executor import AuthorizedGitHubExecutor, GitHubExecutionError
from runtime.orchestrator import AgentProtocolRuntime


class FakeGateway:
    def apply_authorized_change(self, **kwargs):
        return {
            "pull_request": {"number": 42, "html_url": "https://github.com/Yugatn/MyPro/pull/42"},
            "commits": [{"commit": {"sha": "abc123"}}],
        }


def ready_runtime():
    runtime = AgentProtocolRuntime.create()
    kw = {"task_id": "t1", "issuer": "mira", "correlation_id": "c1"}
    for event_type, payload in (
        (EventType.TASK_CREATED, {}),
        (EventType.AGENT_ASSIGNED, {"agent": "grok"}),
        (EventType.WORK_STARTED, {}),
        (EventType.RESULT_PUBLISHED, {"verification_state": "claimed"}),
        (EventType.VERIFICATION_REQUESTED, {}),
        (EventType.VERIFIED, {"verification_state": "independent"}),
        (EventType.PROPOSAL_CREATED, {"verification_state": "verified"}),
        (EventType.DECISION_REQUIRED, {}),
        (EventType.ACTION_AUTHORIZED, {
            "authorization_id": "auth_1",
            "repository": "Yugatn/MyPro",
        }),
    ):
        event = runtime.make_event(event_type=event_type, payload=payload, **kw)
        runtime.ingest(event)
    return runtime, runtime.log.all()[-1]


def test_end_to_end_authorized_github_execution():
    runtime, authorization_event = ready_runtime()
    authorization = GitHubAuthorization(
        "auth_1", "t1", "Yugatn/MyPro", "mira",
        frozenset({"write_branch", "create_pr"}),
        ("spec/", "github/"),
        "main",
    )
    result = AuthorizedGitHubExecutor().execute(
        runtime=runtime,
        authorization=authorization,
        authorization_event=authorization_event,
        branch="mypro/t1",
        base_sha="base123",
        changes=(GitHubChange("spec/example.md", "# changed\n", "create"),),
        pr_title="MyPro authorized change",
        pr_body="Executed through the MyPro GitHub boundary.",
        gateway=FakeGateway(),
    )
    assert result.pull_request["number"] == 42
    assert runtime.state["t1"] is ProtocolState.CHANGED
    events = runtime.log.all()
    assert events[-2].event_type is EventType.GITHUB_CHANGE
    assert events[-1].event_type is EventType.REVISION_RECORDED
    assert events[-1].payload["status"] == "executed"


def test_executor_rejects_wrong_authorization():
    runtime, authorization_event = ready_runtime()
    authorization = GitHubAuthorization(
        "wrong", "t1", "Yugatn/MyPro", "mira",
        frozenset({"write_branch", "create_pr"}), ("spec/",), "main",
    )
    with pytest.raises(GitHubExecutionError):
        AuthorizedGitHubExecutor().execute(
            runtime=runtime,
            authorization=authorization,
            authorization_event=authorization_event,
            branch="mypro/t1",
            base_sha="base123",
            changes=(GitHubChange("spec/example.md", "# changed\n", "create"),),
            pr_title="test",
            pr_body="test",
            gateway=FakeGateway(),
        )
