# Timeline Bridge v0.3

MyPro has one canonical montage semantics with multiple projections.

## Canonical model

MontageModel consists of nodes, edges, rational temporal intervals, track constraints, data dependencies and media references.

## Projections

Track projection orders compatible nodes by track and time. Graph projection preserves dependency relationships without requiring track ordering.

A graph can be represented as a track projection only when it satisfies declared track-decomposability constraints. Otherwise it remains graph-only and the UI must not invent a lossy representation silently.

## Invariants

**I_timeline_projection_preserves_time** — projection does not change canonical temporal intervals.

**I_timeline_dual_edit_consistent** — supported edits through either projection produce the same canonical semantics.
