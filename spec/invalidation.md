# Analysis Invalidation Policy v0.3

Invalidation distinguishes computational freshness from historical truth.

| Entity | Default treatment |
|---|---|
| Observation | invalidate |
| Proposal | mark_stale or invalidate according to policy |
| Decision | never invalidate |
| Revision | never invalidate |
| Render | mark_stale |

A Decision records that a decision was made. Later evidence may make it questionable, but does not rewrite history.

## Bounded cascade

Default invalidation depth is 3. Beyond that depth, dependents are marked stale rather than recursively invalidated unless explicitly authorized.

Every invalidation records the triggering change, affected entity, previous validity state, reason and policy version.

**I_invalidation_bounded** — no invalidation cascade exceeds the configured depth without explicit authorization.
