# MyPro Agent Protocol Runtime v0.1

The runtime is the machine-readable coordination layer between Mira, Grok and other agents.

## Rule
Agents may reason in natural language. The runtime accepts only typed event envelopes. GitHub mutation is a capability behind an explicit authorization event.

## Lifecycle
TASK_CREATED, AGENT_ASSIGNED, WORK_STARTED, RESULT_PUBLISHED, VERIFICATION_REQUESTED, VERIFIED or CONFLICT_DETECTED, PROPOSAL_CREATED, DECISION_REQUIRED, ACTION_AUTHORIZED, GITHUB_CHANGE, REVISION_RECORDED.

## Evidence states
CLAIMED is an agent assertion. OBSERVED is a recorded observation. VERIFIED means independent verification exists. These states are not interchangeable.

## Idempotency
Every event has an event_id and idempotency_key. Replaying an identical event does not append a second event.

## GitHub boundary
The runtime does not contain credentials and does not grant agents GitHub write authority. A GitHubGateway must be explicitly connected; its write method receives an authorization identifier.

## First integration point
Mira can connect to the runtime now for read-only orchestration and event exchange. GitHub write execution becomes available after a concrete GitHubGateway is connected and its authorization path is tested.
