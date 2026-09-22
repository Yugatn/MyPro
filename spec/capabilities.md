# Capability Security v0.3

Capabilities are scoped technical authorities.

Scope matching is segment based. Examples include *, media:*, media:blake3:<hex>, project:<id> and project:<id>:analysis.

Delegation is monotonic: a child capability cannot gain operations or a broader resource scope than its parent. A delegated capability cannot outlive its parent.

A capability is a technical authority, not a policy decision. Policy remains a separate decision layer.

Revocation is checked at use time and does not require restarting Core.

Invariants:
- I_capability_no_amplification
- I_capability_revocable
- I_plugin_capability_bound
