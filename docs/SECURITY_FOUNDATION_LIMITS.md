# SymbiontOS security foundation: verified behavior and limits

## Implemented

The importable public package `core.security` exposes identity anchors, capabilities,
evidence states, policy evaluation, policy decisions, and audit records. Capabilities
match an exact subject, operation, and resource; revoked, expired, not-yet-issued,
and mismatched grants are rejected by the policy evaluation layer. All capability
timestamps must be timezone-aware.

The evidence gate distinguishes VERIFIED from other evidence states when the caller
explicitly requests verified evidence. It does not automatically require evidence
for all operations.

## Not implemented: enforcement authority

This policy kernel is **not** an action executor, credential manager, tamper-proof
evidence registry, trusted verifier registry, or revocation store.

- A caller can construct an arbitrary `Capability` value. An executor must validate
  grants against an authoritative capability store before performing side effects.
- A caller can construct `Evidence(state=VERIFIED)`. An executor must independently
  validate evidence provenance, verifier identity, and trusted verification records.
- An `ALLOW` result by itself does not authorize modifying a repository, sending a
  message, or spending funds.
- In-process immutable dataclasses do not persist or propagate revocation.
- `audit_decision()` creates an audit record in memory; it does not durably append
  one to an independently verifiable audit store.
- A policy decision is descriptive; the trusted enforcement boundary is pending.

Until those integrations exist, external side effects must remain denied by default.
Avoid representing this foundation as a production-safe authorization service.

## Testing

```bash
python -m pytest tests/test_security_foundation.py -q
```

Independent integration tests and CI are required before declaring this module
verified for protected side effects.
