# Concurrency Model v0.3

MyPro uses an append-only event log with a deterministic CRDT-style projection.

Events are immutable. Concurrent events are merged into project state according to explicit, deterministic rules rather than last-write-wins.

## Event identity

Every event should eventually contain:

- event_id;
- actor_id;
- logical clock;
- parent event ids or causal context;
- target entity;
- operation;
- payload;
- schema and ontology versions.

## Merge contract

Independent events may be applied in any order when their operations are declared commutative.

Non-commutative operations require causal dependencies and explicit conflict resolution.

The Core must never silently discard a Decision or Action because another actor wrote later.

## Invariant

**I_event_merge_deterministic** — applying the same compatible event set in different valid orders produces the same projected state.

A Revision identifies the event frontier from which the projection was produced.
