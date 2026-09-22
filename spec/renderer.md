# Renderer Contract v0.3

A renderer consumes an immutable RenderSpecification and returns a render result with provenance. Rendering never mutates canonical project state.

## RenderSpecification

Required fields: render_id, project_revision, montage_view, rational time_range, output requirements, backend hints, quality requirements, proxy/original constraints, and provenance requirements.

The specification is the contract between Evidence Core and FFmpeg, MLT, native hardware or remote backends.

## Result

A RenderResult records render id, input revision, output asset hash, backend and encoder identity/version, execution environment, quality measurements, provenance and declared tolerance.

## Conformance

A backend claiming Renderer Contract v1 must pass the common conformance suite. Bit-identical output is required where deterministic encoding is declared; otherwise an explicit comparison tolerance is required.

## Invariants

**I_renderer_no_state_mutation** — rendering cannot mutate canonical project state.

**I_renderer_deterministic_given_spec** — a deterministic backend produces reproducible output for the same specification and execution context.
