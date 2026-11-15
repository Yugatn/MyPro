import pytest

from protocol.event_log import EventConflict
from protocol.events import EventEnvelope, EventType
from protocol.state_machine import ProtocolState
from protocol.validation import ProtocolViolation
from runtime.orchestrator import AgentProtocolRuntime


def test_machine_lifecycle_reaches_action_ready():
    runtime = AgentProtocolRuntime.create()
    kw = dict(task_id="t1", issuer="mira", correlation_id="c")

    runtime.ingest(runtime.make_event(
        event_type=EventType.TASK_CREATED,
        payload={"task_kind": "repo_change"},
        **kw,
    ))
    runtime.ingest(runtime.make_event(
        event_type=EventType.AGENT_ASSIGNED,
        payload={"agent": "grok"},
        **kw,
    ))
    runtime.ingest(runtime.make_event(event_type=EventType.WORK_STARTED, payload={}, **kw))
    runtime.ingest(runtime.make_event(
        event_type=EventType.RESULT_PUBLISHED,
        payload={"result_id": "r1", "verification_state": "claimed"},
        **kw,
    ))
    runtime.ingest(runtime.make_event(
        event_type=EventType.VERIFICATION_REQUESTED,
        payload={"verification_id": "vr1"},
        **kw,
    ))
    runtime.ingest(runtime.make_event(
        event_type=EventType.VERIFIED,
        payload={
            "verification_id": "v1",
            "verifier": "grok",
            "verification_state": "independent",
        },
        **kw,
    ))
    runtime.ingest(runtime.make_event(
        event_type=EventType.PROPOSAL_CREATED,
        payload={"proposal_id": "p1", "verification_state": "verified"},
        **kw,
    ))
    runtime.ingest(runtime.make_event(
        event_type=EventType.DECISION_REQUIRED,
        payload={"decision_id": "d1"},
        **kw,
    ))
    assert runtime.ingest(runtime.make_event(
        event_type=EventType.ACTION_AUTHORIZED,
        payload={
            "authorization_id": "a1",
            "authorized_by": "human",
            "decision_id": "d1",
        },
        **kw,
    )) is ProtocolState.ACTION_READY


def test_duplicate_event_is_idempotent():
    runtime = AgentProtocolRuntime.create()
    event = runtime.make_event(
        event_type=EventType.TASK_CREATED,
        task_id="t",
        issuer="mira",
        correlation_id="c",
        payload={"task_kind": "repo_change"},
    )
    assert runtime.ingest(event) is ProtocolState.NEW
    assert runtime.ingest(event) is ProtocolState.NEW
    assert len(runtime.log.all()) == 1


def test_event_id_collision_is_rejected():
    runtime = AgentProtocolRuntime.create()
    first = runtime.make_event(
        event_type=EventType.TASK_CREATED,
        task_id="t",
        issuer="mira",
        correlation_id="c",
        payload={"task_kind": "repo_change"},
    )
    conflicting = EventEnvelope(
        event_id=first.event_id,
        event_type=EventType.TASK_CREATED,
        task_id="t",
        issuer="mira",
        correlation_id="c",
        idempotency_key="different",
        payload={"task_kind": "different"},
        schema_version="0.2",
    )
    runtime.ingest(first)
    with pytest.raises((EventConflict, ValueError)):
        runtime.ingest(conflicting)


def test_github_change_requires_explicit_authorization_data():
    runtime = AgentProtocolRuntime.create()
    runtime.state["t"] = ProtocolState.ACTION_READY
    event = runtime.make_event(
        event_type=EventType.GITHUB_CHANGE,
        task_id="t",
        issuer="mira",
        correlation_id="c",
        payload={"authorized": True},
    )
    with pytest.raises(ProtocolViolation):
        runtime.ingest(event)


def test_event_payload_is_a_deep_immutable_snapshot():
    runtime = AgentProtocolRuntime.create()
    original = {"task_kind": "repo_change", "context": {"paths": ["README.md"]}}
    event = runtime.make_event(
        event_type=EventType.TASK_CREATED,
        task_id="immutable",
        issuer="mira",
        correlation_id="c",
        payload=original,
    )
    digest_before = event.canonical_json()
    original["context"]["paths"].append("tampered.py")

    assert event.payload["context"]["paths"] == ("README.md",)
    assert event.canonical_json() == digest_before
    with pytest.raises(TypeError):
        event.payload["context"]["other"] = "tamper"

    copy = event.as_dict()
    copy["payload"]["context"]["paths"].append("tampered-again.py")
    assert event.canonical_json() == digest_before
    assert runtime.ingest(event) is ProtocolState.NEW


def test_github_change_accepts_frozen_nested_changes():
    runtime = AgentProtocolRuntime.create()
    runtime.state["t"] = ProtocolState.ACTION_READY
    changes = [{"path": "README.md", "action": "update"}]
    event = runtime.make_event(
        event_type=EventType.GITHUB_CHANGE,
        task_id="t",
        issuer="mira",
        correlation_id="c",
        payload={
            "authorization_id": "authorization-1",
            "change_id": "change-1",
            "repository": "Yugatn/MyPro",
            "changes": changes,
        },
    )
    changes[0]["path"] = "malicious-path"
    assert event.payload["changes"][0]["path"] == "README.md"
    assert runtime.ingest(event) is ProtocolState.CHANGED
