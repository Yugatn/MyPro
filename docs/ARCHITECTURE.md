# Architecture

## 1. Core thesis

MyPro is a verifiable content and decision environment, not merely a video editor.

The canonical architecture separates:

1. content identity;
2. observations;
3. interpretations;
4. findings;
5. proposals;
6. decisions;
7. applied actions;
8. recoverable revisions.

This prevents AI, analyzers or UI code from silently becoming the source of truth.

## 2. Layer boundaries

### Identity and Media

Identifies Assets and records technical metadata, hashes, external references and proxy relationships.

### Analysis

Runs analyzers as versioned computations. The analysis layer produces observations and findings, not silent project mutations.

The intended execution model is a DAG. Each node declares its analyzer identity, version, code hash, configuration hash, input artifacts and output artifacts. This supports caching and invalidation.

Cinema Catharsis is a domain measurement layer in Analysis. It operates on the same observations and exact time ranges as MyPro fragments and reports descriptive content metrics without silently inferring viewer response or harm.

### Evidence and Provenance

Evidence connects results to their source and derivation. Provenance is content-addressed where practical and may map to C2PA and W3C PROV.

### Project

The project has a schema version, append-only event history, snapshots and explicit migration boundaries.

### Montage

Montage Model is the canonical editable representation of tracks, clips, timing, transitions, audio, subtitles, effects and markers.

External interchange formats do not replace the canonical model.

### AI

AI consumes project context and analysis and produces explicit Proposal objects. AI does not directly mutate canonical project state.

### Runtime and Security

Extensions run behind capability boundaries. Default policy is deny by default. Sensitive operations are mediated by Core.

### Applications

Desktop, mobile, CLI and future research/security applications consume the same core contracts.

## 3. Formal control boundary

**AI or analyzer proposes. Core validates. Human or policy decides. Action applies. Project records.**

For low-risk workflows, a policy may authorize automatic application. Such automation must still create an auditable decision and a recoverable revision.

## 4. Time model

Canonical project time uses exact rational values. Intervals are half-open, written conceptually as [start, end).

Adapters may expose frame, audio-sample, nanosecond or float-second representations, but conversions must be explicit and deterministic.

The model must eventually cover VFR, drop-frame timecode, audio sample time, multi-camera synchronization and external sensor synchronization.

## 5. Project persistence

The project format is designed around:

- append-only JSONL events;
- periodic snapshots;
- content-addressed derived artifacts;
- atomic writes;
- explicit schema versions;
- deterministic migrations;
- recoverable backups.

A migration that can replace canonical state must first establish a verified recovery point.

## 6. Analysis semantics

An Observation carries:

- value;
- confidence;
- uncertainty;
- status;
- analyzer identity;
- provenance.

not_analyzed, failed and unknown are meaningful states. They must not be silently treated as negative evidence.

Domain formulas declare their inputs, assumptions, version, valid domain, output semantics and uncertainty behavior. MyPro does not define one universal risk score.

Cinema Catharsis follows the same boundary. Its metrics describe coded media content and coding quality. They do not constitute automatic estimates of viewer emotion, audience attitude, psychological harm or causal effect.

## 7. Plugin security

Capabilities are scoped by resource and operation. Future runtime implementations may use WASM and/or process isolation.

Baseline controls:

- deny by default;
- explicit network capability;
- resource-scoped access;
- signed plugins for trusted distribution;
- dependency pinning and SBOM;
- capability audit log;
- malformed-media and parser fuzzing.

A capability grants technical authority only within its declared scope. Policy remains a separate layer.

## 8. Interoperability

- FFprobe populates MediaManifest technical data.
- FFmpeg is an external media backend.
- OpenTimelineIO is an editorial interchange boundary.
- C2PA is a provenance interoperability target.
- W3C PROV provides provenance mapping concepts.
- MLT may become a rendering backend.
- EDL/XML/AAF are explicit import/export boundaries.

See docs/INTEROP.md.

## 9. Privacy

Local-first processing is preferred. Network access is explicit. Sensitive processing should be minimized, scoped and auditable.

See docs/PRIVACY.md and docs/THREAT_MODEL.md.

## 10. Verification

The architecture is defined by executable invariants rather than comments alone. The initial invariant catalogue is in spec/invariants.md.

Future verification work includes:

- property-based tests;
- parser fuzzing;
- TLA+ models for atomicity and capability semantics;
- reproducible builds;
- golden datasets for analysis;
- deterministic replay of project events.
