# Roadmap

## Phase 0 — Foundation

- [x] Repository structure
- [x] Formal ontology
- [x] Project/observation/proposal/capability schemas
- [x] Rational time primitive
- [x] Append-only event log primitive
- [x] Versioned observation primitive
- [x] Provenance, privacy and threat-model specifications
- [ ] Media Manifest v0.2
- [ ] FFprobe Media Probe
- [ ] Atomic project persistence
- [ ] Snapshot/recovery mechanism
- [ ] Backup verification and restore
- [ ] CI invariant checks

## Phase 1 — Evidence

- [ ] Analysis DAG
- [ ] Analyzer registry
- [ ] Provenance graph
- [ ] Incremental analysis cache
- [ ] Plugin SDK
- [ ] Capability scopes
- [ ] WASM/process isolation
- [ ] Evidence bundle export
- [ ] C2PA mapping

## Phase 2 — Montage

- [ ] Canonical Montage Model v0.2
- [ ] Exact timeline operations
- [ ] Multi-track editing
- [ ] Audio and subtitle model
- [ ] OTIO interchange
- [ ] Render specification
- [ ] Basic desktop editor

## Phase 3 — AI

- [ ] Proposal Engine
- [ ] Policy boundary
- [ ] Human-in-the-loop review
- [ ] Reversible action system
- [ ] AI rough-cut pipeline
- [ ] RosEdit desktop

## Phase 4 — Ecosystem

- [ ] Mobile client
- [ ] Security Analyzer
- [ ] EthicalAudit integration
- [ ] РосЭкшн integration
- [ ] RosAction integration
- [ ] Plugin SDK and distribution
- [ ] Collaboration

## Verification track

Across all phases:

- property-based tests;
- fuzzing;
- deterministic replay;
- dependency/SBOM checks;
- invariant regression tests;
- reproducible builds where practical.

## Principle

Every phase must leave behind a usable, testable subsystem. UI features should not outrun the model, persistence and verification layers underneath them.
