# Policy Engine v0.3

Policy is a deterministic authorization and automation layer. It is distinct from capability.

A capability answers whether a component technically can perform an operation. Policy answers whether the operation is permitted in the current context.

## Policy object

A policy declares:

- policy_id;
- version;
- scope;
- rules;
- provenance;
- effective revision.

Rules must have deterministic evaluation semantics.

## Action gate

Before an Action is applied, Core evaluates:

1. schema validity;
2. current revision;
3. capability scope;
4. applicable policy;
5. invariant preconditions.

The evaluation itself becomes provenance.

## Automatic actions

A policy may authorize automatic application of a defined low-risk operation. Such actions remain auditable and recoverable.

## Invariant

**I_policy_applied_before_action** — no Action reaches canonical project state without a recorded applicable Policy evaluation.
