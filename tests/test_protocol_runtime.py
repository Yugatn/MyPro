import pytest
from protocol.events import EventType
from protocol.state_machine import ProtocolState
from protocol.validation import ProtocolViolation
from runtime.orchestrator import AgentProtocolRuntime

def test_machine_lifecycle_reaches_action_ready():
    r=AgentProtocolRuntime.create(); kw=dict(task_id="t1",issuer="mira",correlation_id="c")
    r.ingest(r.make_event(event_type=EventType.TASK_CREATED,payload={**{}},**kw))
    r.ingest(r.make_event(event_type=EventType.AGENT_ASSIGNED,payload={"agent":"grok"},**kw))
    r.ingest(r.make_event(event_type=EventType.WORK_STARTED,payload={},**kw))
    r.ingest(r.make_event(event_type=EventType.RESULT_PUBLISHED,payload={"verification_state":"claimed"},**kw))
    r.ingest(r.make_event(event_type=EventType.VERIFICATION_REQUESTED,payload={},**kw))
    r.ingest(r.make_event(event_type=EventType.VERIFIED,payload={"verification_state":"independent"},**kw))
    r.ingest(r.make_event(event_type=EventType.PROPOSAL_CREATED,payload={"verification_state":"verified"},**kw))
    r.ingest(r.make_event(event_type=EventType.DECISION_REQUIRED,payload={},**kw))
    assert r.ingest(r.make_event(event_type=EventType.ACTION_AUTHORIZED,payload={},**kw)) is ProtocolState.ACTION_READY

def test_duplicate_event_is_idempotent():
    r=AgentProtocolRuntime.create(); e=r.make_event(event_type=EventType.TASK_CREATED,task_id="t",issuer="mira",correlation_id="c",payload={})
    assert r.ingest(e) is ProtocolState.NEW
    assert r.ingest(e) is ProtocolState.NEW
    assert len(r.log.all())==1

def test_github_change_requires_authorization():
    r=AgentProtocolRuntime.create(); kw=dict(task_id="t",issuer="mira",correlation_id="c")
    r.state["t"]=ProtocolState.ACTION_READY
    e=r.make_event(event_type=EventType.GITHUB_CHANGE,payload={"authorized":False},**kw)
    with pytest.raises(ProtocolViolation): r.ingest(e)
