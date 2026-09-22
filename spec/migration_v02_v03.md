# Migration v0.2 to v0.3

Migration is explicit, versioned and testable.

Planned transformations:

1. Ontology 0.2.x to 0.3.x.
2. Project format v1 to v2 with event and snapshot structures.
3. Observation schema v1 to v2 with explicit analysis status.
4. Capability model from flat grants to scoped, expiring, revocable grants.

Each migration is a named function with fixture corpus and semantic checks.

A migration declares source version, target version, reversible, lossy, preconditions and transformation rules.

Projects newer than the supported reader version are not silently downgraded.

**I_migration_reversible** — migrations marked reversible can restore the prior representation without semantic loss.
