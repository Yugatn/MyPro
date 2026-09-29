from runtime.checkpoint import BoundedExecutionPolicy, CheckpointStore, ExecutionCheckpoint


def test_checkpoint_round_trip(tmp_path):
    store = CheckpointStore(tmp_path / "checkpoint.json")
    original = ExecutionCheckpoint(task_id="t1", phase="VERIFY", last_completed_step="ci_status_checked", next_step="inspect_failed_job", known_facts=("PR #16 is open",), completed_calls=("pr_metadata", "ci_status"), files_changed=("runtime/checkpoint.py",), tests_status="pass", ci_status="fail", attempt=2)
    store.save(original)
    assert store.load() == original


def test_checkpoint_write_is_atomic_from_reader_perspective(tmp_path):
    store = CheckpointStore(tmp_path / "checkpoint.json")
    checkpoint = ExecutionCheckpoint(task_id="t1", phase="DIAGNOSE", last_completed_step="pr_read", next_step="ci_read")
    store.save(checkpoint)
    assert store.path.exists()
    assert not store.path.with_suffix(".json.tmp").exists()


def test_bounded_policy_skips_completed_calls():
    policy = BoundedExecutionPolicy(max_calls_per_tranche=3)
    assert policy.select_next(completed_calls={"pr_metadata", "ci_status"}, candidates=["pr_metadata", "ci_status", "failed_job"]) == "failed_job"



def test_runtime_can_resume_checkpoint(tmp_path):
    from runtime.orchestrator import AgentProtocolRuntime

    store = CheckpointStore(tmp_path / "checkpoint.json")
    runtime = AgentProtocolRuntime.create(checkpoint_store=store)
    checkpoint = ExecutionCheckpoint(
        task_id="t1",
        phase="VERIFY",
        last_completed_step="ci_status_checked",
        next_step="inspect_failed_job",
        completed_calls=("pr_metadata", "ci_status"),
    )
    runtime.save_checkpoint(checkpoint)
    resumed = runtime.resume_checkpoint("t1")
    assert resumed == checkpoint
    assert runtime.resume_checkpoint("other") is None



def test_bounded_policy_selects_at_most_configured_batch():
    policy = BoundedExecutionPolicy(max_calls_per_tranche=2)
    assert policy.select_batch(
        completed_calls=set(), candidates=["a", "b", "c"]
    ) == ("a", "b")


def test_bounded_policy_refuses_execution_after_limit():
    policy = BoundedExecutionPolicy(max_calls_per_tranche=2)
    assert policy.can_execute(calls_in_tranche=1)
    assert not policy.can_execute(calls_in_tranche=2)
    try:
        policy.require_capacity(calls_in_tranche=2)
    except RuntimeError as exc:
        assert "exhausted" in str(exc)
    else:
        raise AssertionError("expected bounded tranche exhaustion")
