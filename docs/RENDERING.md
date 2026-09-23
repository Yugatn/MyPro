# FFmpeg Render Backend

The Foundation renderer is deliberately separated from project state.

A render consumes a MontageRepository snapshot and an immutable RenderSpecification. It builds a deterministic FFmpeg command. Execution is optional, so command generation can be tested without an FFmpeg installation.

## Current scope

- layered video composition;
- deterministic filter graph generation;
- rational timeline duration converted only at the FFmpeg boundary;
- explicit codec, pixel format, dimensions and frame rate;
- output hashing after a successful render;
- render specification and result hashes for provenance.

The first backend slice is video-only. Audio layers require a future explicit mix policy and are not silently discarded by a caller that supplies them to a backend configured with audio_policy=reject.

## State boundary

The renderer does not append project events, mutate timelines, or alter media manifests. The caller owns the resulting RenderResult and may persist it as a provenance artifact.

## Future extensions

- audio mixdown with gain and pan;
- source in/out ranges separate from timeline ranges;
- blend modes and masks;
- hardware encoder capability discovery;
- C2PA signing;
- conformance renders using generated test media.
