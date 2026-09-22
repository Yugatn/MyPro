# Capability Security v0.3

Capabilities are scoped technical authorities.

A capability declares:

- capability id;
- subject;
- resource scope;
- operations;
- issued_at;
- expires_at;
- revocable;
- delegable;
- parent capability when delegated.

## Scope

Resource scope should be as narrow as practical, for example a specific asset hash rather than an entire filesystem.

## Revocation

Core maintains revocation state and checks it at sensitive operations. Revocation does not require restarting Core.

## Delegation

Delegation can only narrow authority. A child capability cannot gain operations, resources or lifetime broader than its parent.

## Invariants

**I_capability_no_amplification** — delegation cannot increase authority.

**I_capability_revocable** — an active capability can be denied before expiry.

**I_plugin_capability_bound** — operations outside the granted scope are rejected.
