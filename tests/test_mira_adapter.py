from ai.mira_adapter import MiraAdapter, MiraResult, MiraTask

def test_consumes_verified_grok_result():
    a=MiraAdapter(); t=MiraTask("t1","finish")
    r=MiraResult("r1","t1","grok","completed","done",evidence=({"kind":"commit","value":"abc"},),verification_state="verified")
    s=a.consume_grok_results(t,[r])
    assert s["status"]=="verified" and s["next_action"]=="create_proposal"

def test_child_task_is_idempotent():
    a=MiraAdapter(); t=MiraTask("root","complete",correlation_id="c")
    x=a.create_remaining_work_task(t,remaining_objective="missing",assigned_agent="mira")
    y=a.create_remaining_work_task(t,remaining_objective="missing",assigned_agent="mira")
    assert x.task_id==y.task_id and x.idempotency_key==y.idempotency_key

def test_conflict_is_preserved():
    a=MiraAdapter(); t=MiraTask("t1","verify")
    x=MiraResult("a","t1","grok","completed","x",claims=({"category":"OBSERVED","statement":"status=ready"},))
    y=MiraResult("b","t1","grok","completed","y",claims=({"category":"OBSERVED","statement":"status=blocked"},))
    s=a.consume_grok_results(t,[x,y])
    assert s["status"]=="conflict" and s["next_action"]=="independent_verification"

def test_proposal_requires_verification():
    a=MiraAdapter(); t=MiraTask("t1","finish")
    r=MiraResult("g","t1","grok","completed","done",evidence=({"kind":"commit","value":"abc"},),verification_state="verified")
    p=a.create_proposal(t,[r],changes=({"operation":"add_file","path":"x"},),intent="integrate verified work")
    assert p.requires_decision and p.verification_state=="verified"
