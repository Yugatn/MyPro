# Mira AI Interaction Algorithm v0.1

**Status:** implementation-oriented specification  
**Purpose:** define a deterministic, auditable interaction protocol between the MyPro Control Plane and named AI agents, with **Mira** as the coordinating agent and **Grok** as an independent worker/verifier when assigned.

## 1. Core rule

Mira does not treat another agent's message as truth. Every inter-agent statement is a claim until it is connected to evidence and, where required, independently verified.

The interaction boundary is:

**task → assignment → execution → result → evidence → verification → proposal → decision → action → revision**

An AI agent may propose work or produce an artifact. It may not silently mutate canonical project state.

## 2. Roles

### Mira

Logical agent identifier: `mira`.

Default role: coordinator / synthesis agent.

Mira:
- decomposes the user's objective into bounded tasks;
- assigns work to available agents;
- reads existing evidence before requesting duplicate work;
- compares independent results;
- marks unresolved conflicts;
- produces a Proposal for the MyPro AI layer;
- never treats its own synthesis as independent verification.

### Grok

Logical agent identifier: `grok`.

Default role: independent engineering worker / verifier.

Grok:
- performs explicitly assigned implementation or verification tasks;
- publishes machine-readable results;
- attaches commit, blob, test, or evidence references;
- reports limitations and untested areas;
- does not silently redefine task scope.

The role labels are defaults, not permissions. Capability and policy remain separate.

## 3. Required task lifecycle

1. **Receive objective.** Mira receives a user objective and creates a stable `task_id`.
2. **Load context.** Mira resolves relevant project state, constraints, prior results and evidence.
3. **Decompose.** The objective is split into atomic subtasks with explicit expected outputs.
4. **Assign.** A subtask is assigned to Mira, Grok, another agent, or a human.
5. **Execute.** The assigned agent works only within declared capabilities.
6. **Publish result.** The agent publishes a result envelope containing claims, artifacts, tests and uncertainty.
7. **Check evidence.** References are resolved and hashes are checked when available.
8. **Verify.** A different execution or agent verifies work when the task requires independent verification.
9. **Reconcile.** Mira compares results. Compatible observations are combined; incompatible observations create a conflict.
10. **Propose.** Mira creates a MyPro Proposal containing the intended project change and provenance.
11. **Policy gate.** The policy layer evaluates whether the proposal is allowed.
12. **Decision.** A human or authorized policy creates an explicit Decision.
13. **Action.** Only an authorized action handler mutates project state.
14. **Revision.** The resulting state and provenance are appended to the event history.
15. **Report.** Mira reports what was observed, what was derived, what remains uncertain, and what was actually changed.

## 4. Grok handoff rule

When Grok has already completed part of the work, Mira MUST first attempt to consume that result rather than recreating the work.

Minimum handoff record:

- `task_id`
- `agent_id = grok`
- `result_id`
- `status`
- `artifacts`
- `evidence`
- `claims`
- `tests_performed`
- `verification_state`
- `uncertainty`
- `requested_next_action`

If the result is only a textual assertion and has no resolvable artifact/evidence reference, Mira may use it as context but must label it **CLAIMED**.

## 5. Independent verification

For tasks marked `independent` or `dual` verification:

- Mira MUST NOT verify a result solely by repeating the same reasoning path.
- Grok MUST NOT be the sole verifier of its own implementation.
- A second execution, distinct agent, deterministic test suite, or human review must provide the independent check.
- Agreement between Mira and Grok is not itself evidence of correctness.

## 6. Conflict handling

If two results contain incompatible OBSERVED claims for the same task:

1. preserve both results;
2. emit `CONFLICT_DETECTED`;
3. do not silently select a winner;
4. request independent verification;
5. if unresolved and consequential, require human authorization;
6. record the final decision and its evidence.

A conflict is a state to be resolved, not an error to be hidden.

## 7. Failure and retry

Retries use the same `task_id` and a stable `idempotency_key` for the same intended side effect.

A retry MUST NOT:
- duplicate an already completed side effect;
- overwrite a newer result without an explicit supersession relation;
- convert an access failure into an object-absence claim.

If an agent is unavailable, Mira may reassign the task only if the task's policy permits reassignment.

## 8. Authority boundary

The following statements are deliberately different:

- an agent produced a result;
- an artifact exists;
- an artifact was tested;
- an artifact was independently verified;
- a proposal was accepted;
- an action was authorized;
- an action was executed.

Mira must preserve these distinctions in its output.

## 9. Reference implementation contract

The reference implementation in `ai/agent_interaction.py` is intentionally deterministic and side-effect free. It decides the next protocol state from envelopes; it does not call an LLM, GitHub, filesystem, or external network.

External adapters can wrap this state machine later.

## 10. Example

User objective:

> "Complete the remaining implementation of the current feature using the work Grok already performed."

Mira:

1. locates Grok's result;
2. validates its references;
3. identifies the remaining unimplemented task;
4. creates a new child task linked to Grok's result;
5. assigns the missing implementation to the appropriate agent;
6. runs independent tests;
7. creates a Proposal from verified evidence;
8. waits for the required Decision;
9. applies the Action only after authorization;
10. reports exactly which parts came from Grok, which were independently verified, and which remain unverified.

## 11. Non-goals

This specification does not define:
- a vendor-specific Mira API;
- a vendor-specific Grok API;
- model selection;
- prompts as an authority mechanism;
- automatic permission escalation;
- autonomous irreversible project changes.

Those concerns belong to adapters, capabilities and policy.
