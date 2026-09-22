# Migration v0.2 to v0.3

Migration is explicit, versioned, deterministic and backup-first.

A migration declares source version, target version, reversibility and lossiness. The registry rejects undeclared transformations and refuses to silently downgrade newer projects.

Before destructive replacement, the caller must create a verified recovery point. Migration output must declare the target schema version.

The initial registry is intentionally small. Unsupported transformations fail closed until their semantic mapping is implemented and tested.
