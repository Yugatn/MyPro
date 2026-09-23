# MyPro Agent Protocol Runtime v0.2

The runtime is the machine-readable coordination layer between Mira, Grok and other agents.

## Safety boundary

Agents may reason in natural language, but the runtime accepts only typed event envelopes. The runtime records proposals and authorization state; it does not treat an agent assertion as a verified fact.

GitHub mutation is represented by an explicit authorization payload containing an authorization identifier, decision identifier, repository and concrete changes.

## Lifecycle

TASK_CREATED, AGENT_ASSIGNED, WORK_STARTED, RESULT_PUBLISHED, VERIFICATION_REQUESTED, VERIFIED or CONFLICT_DETECTED, PROPOSAL_CREATED, DECISION_REQUIRED, ACTION_AUTHORIZED, GITHUB_CHANGE, REVISION_RECORDED.

## Evidence states

CLAIMED is an agent assertion. OBSERVED is a recorded observation. VERIFIED requires an independent verifier. These states are not interchangeable.

## Idempotency

Every event has an event_id and idempotency_key. Replaying the exact same event is a no-op. Reusing either identifier for different content is a protocol conflict.

## Atomicity

The runtime computes the next state before committing it. The event is appended before in-memory state is changed, so an idempotency conflict cannot partially mutate runtime state.

## GitHub boundary

The protocol runtime does not contain credentials and does not grant agents GitHub write authority. A concrete GitHubGateway remains an integration boundary. The gateway receives an explicit authorization identifier rather than an implicit boolean permission.

## Versioning

Event Envelope v0.2 is the active runtime contract. The schema is stored at `schemas/event-envelope.v0.2.schema.json`.