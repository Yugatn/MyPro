from ai.agent_interaction import (
    AgentResult,
    InteractionState,
    next_state,
)


def test_mira_loads_context_before_assignment():
    assert next_state(current=InteractionState.RECEIVED).state is InteractionState.CONTEXT_LOADING
    assert next_state(current=InteractionState.CONTEXT_LOADING).state is InteractionState.READY_FOR_ASSIGNMENT
    assert next_state(current=InteractionState.READY_FOR_ASSIGNMENT).state is InteractionState.ASSIGNED


def test_grok_result_requires_verification():
    result = AgentResult(
        agent_id="grok",
        status="completed",
        has_evidence=True,
        verification_state="unverified",
    )
    decision = next_state(current=InteractionState.RUNNING, results=[result])
    assert decision.state is InteractionState.RESULT_PENDING_VERIFICATION


def test_verified_result_becomes_proposal():
    result = AgentResult(
        agent_id="grok",
        status="completed",
        has_evidence=True,
        verification_state="verified",
    )
    assert next_state(
        current=InteractionState.RUNNING, results=[result]
    ).state is InteractionState.VERIFIED
    assert next_state(
        current=InteractionState.VERIFIED, results=[result]
    ).state is InteractionState.PROPOSAL_READY


def test_conflict_never_auto_selects():
    result = AgentResult(
        agent_id="grok",
        status="completed",
        has_evidence=True,
        verification_state="conflicted",
        has_conflict=True,
    )
    decision = next_state(current=InteractionState.RUNNING, results=[result])
    assert decision.state is InteractionState.CONFLICT
