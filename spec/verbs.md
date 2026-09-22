# Typed Verbs v0.3

MyPro exposes a finite, versioned vocabulary of typed operations. MCP schemas are generated from these contracts; MCP is not the source of truth.

## Observation verbs

- observe.media_metadata
- observe.scene_boundaries
- observe.speech_segments
- observe.duplicates
- observe.quality
- observe.provenance

Observation verbs cannot mutate canonical state.

## Proposal verbs

- propose.montage
- propose.cut
- propose.remove_duplicate
- propose.auto_reframe
- propose.generate_broll
- propose.restructure

Proposal verbs create Proposal objects only.

## Decision verbs

- decide.accept
- decide.reject
- decide.modify
- decide.defer

Decision verbs create explicit Decision events.

## Action verbs

- apply
- revert
- checkpoint

The apply operation is Core-controlled. Agents cannot bypass Policy and capability validation.

## Addressing

Verbs use stable asset_id, artifact_id and revision_hash identifiers. They do not accept arbitrary filesystem URIs.

## Invariants

**I_verb_no_direct_mutation** — Observation and Proposal verbs cannot mutate canonical state.

**I_verb_schema_pinned** — an externally exposed verb must exist in the versioned MyPro verb specification.
