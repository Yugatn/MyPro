# MyPro Resumable Bounded Execution v0.1

## Purpose

MyPro keeps agent work resumable when an external agent reaches a usage limit, disconnects, or stops between tool calls. The task state is preserved separately from the agent session.

## Checkpoint contract

A checkpoint records: task identity, phase, last completed step, exactly the next intended step, known facts, evidence references, completed tool-call labels, changed files, test and CI status, and attempt number.

A resume operation must consume the checkpoint before making a new diagnostic call.

## Bounded execution

A tranche is intentionally small. The default maximum is three tool-call labels. The limit applies to the current tranche, not to the task as a whole.

The executor must not repeat a call already present in completed_calls unless new evidence invalidates the previous result.

## Resume invariant

Usage exhaustion is not task failure. The next agent starts from the checkpoint, known facts, remaining work, and one next action. It does not restart diagnosis from zero.

## Security

A checkpoint may contain evidence references and operational state, but must never contain access tokens, passwords, private keys, or raw authorization credentials. GitHub authorization remains governed by the existing ACTION_AUTHORIZED flow.

## PR #16 integration

The resumable layer is deliberately independent of the GitHub gateway. It can resume diagnosis, testing, verification, or reporting without gaining any new GitHub authority.

## Expected report

STATUS: COMPLETE | BLOCKED
PR: #16
CI: PASS | FAIL | RUNNING
PHASE: DIAGNOSE | FIX | VERIFY | REPORT
NEXT_ACTION: one concrete action
CHECKPOINT: task checkpoint identifier
