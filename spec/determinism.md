# Determinism Contract v0.3

Determinism is a declared property, not an assumption.

## Analyzer classes

Every analyzer declares one of:

- deterministic;
- seed_reproducible;
- nondeterministic.

The declaration is part of analyzer provenance.

## Reproducibility context

A reproducible result records, where relevant:

- analyzer version;
- code hash;
- configuration hash;
- model identity/version;
- model weights hash;
- runtime/library versions;
- environment hash;
- random seed;
- input hashes.

## Replay

A deterministic computation must produce the same canonical result for the same declared execution context.

Seed-reproducible computation must record the seed and all required execution identity.

Nondeterministic analysis may still be useful, but it cannot silently become an irreversible Action.

## Invariant

**I_replay_deterministic_for_class** — CI verifies the declared determinism class on a reference corpus.
