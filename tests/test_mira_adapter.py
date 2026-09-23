from ai.mira_adapter import MiraAdapter, MiraResult, MiraTask


def test_mira_consumes_grok_result_without_repeating_work():
    adapter = MiraAdapter()
    task = MiraTask(
        task_id="task_root",
        objective="finish feature",
        correlation_id="corr_1",
        idempotency_key="idem_root",
    )
    result = MiraResult(
        result_id="result_grok_1",
        task_id="task_root",
        agent_id="grok",
        status="completed",
        summary="implemented foundation",
        verification_state="verified",
        evidence=({"kind": "commit", "value": "abc123"},),
    )

    state = adapter.consume_grok_results(task, [result])
    assert state["status"] == "verified"
    assert state["next_action"] == "create_proposal"
    assert state["verified_result_ids"] == ("result_grok_1",)


def test_mira_creates_deterministic_remaining_work_task():
    adapter = MiraAdapter()
    parent = MiraTask(
        task_id="root",
        objective="complete project",
        correlation_id="corr",
        idempotency_key="idem",
    )
    a = adapter.create_remaining_work_task(
        parent,
        remaining_objective="implement missing adapter",
        assigned_agent="mira",
    )
    b = adapter.create_remaining_work_task(
        parent,
        remaining_objective="implement missing adapter",
        assigned_agent="mira",
    )
    assert a.task_id == b.task_id
    assert a.idempotency_key == b.idempotency_key
    assert a.parent_task_id == "root"


def test_mira_preserves_conflict():
    adapter = MiraAdapter()
    task = MiraTask(
        task_id="root",
        objective="verify",
        correlation_id="corr",
        idempotency_key="idem",
    )
    results = [
        MiraResult(
            result_id="a",
            task_id="root",
            agent_id="grok",
            status="completed",
            summary="x",
            claims=({"category": "OBSERVED", "statement": "status=ready"},),
        ),
        MiraResult(
            result_id="b",
            task_id="root",
            agent_id="grok",
            status="completed",
            summary="y",
            claims=({"category": "OBSERVED", "statement": "status=blocked"},),
        ),
    ]
    state = adapter.consume_grok_results(task, results)
    assert state["status"] == "conflict"
    assert state["next_action"] == "independent_verification"


def test_proposal_requires_verified_evidence():
    adapter = MiraAdapter()
    task = MiraTask(
        task_id="root",
        objective="finish",
        correlation_id="corr",
        idempotency_key="idem",
    )
    result = MiraResult(
        result_id="g",
        task_id="root",
        agent_id="grok",
        status="completed",
        summary="done",
        verification_state="verified",
        evidence=({"kind": "commit", "value": "abc"},),
    )
    proposal = adapter.create_proposal(
        task,
        [result],
        changes=({"operation": "add_file", "path": "example"},),
        intent="integrate verified implementation",
    )
    assert proposal.requires_decision is True
    assert proposal.verification_state == "verified"
    assert proposal.source_result_ids == ("g",)
