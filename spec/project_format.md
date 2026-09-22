# Project Format v2

The project format is designed around append-only events, content-addressed artifacts and recoverable snapshots.

A project directory has the following conceptual layout:

```text
project.mypro/
├── manifest.json
├── events.jsonl
├── snapshots/
├── media/
├── analysis/
├── montage/
├── provenance/
├── backups/
└── locks/
```

## Canonical state

The event log is the authoritative history of project mutations. Snapshots are materialized states used to accelerate opening and recovery.

Events are immutable records. A correction is represented by a new event, never by silently rewriting an old event.

## Content addressing

Every persisted artifact that participates in provenance SHOULD have a content hash. SHA-256 is the baseline interoperability hash. BLAKE3 MAY be added as an additional digest where available.

Hashes identify content; they do not by themselves establish trust.

## Atomic persistence

A successful project write must either preserve the previous valid state or install a complete new state. Temporary files, flushes and atomic rename are implementation details of this invariant.

## Schema evolution

Every persisted schema has an explicit version. Migrations are deterministic, documented and testable. A migration must create a recoverable backup before destructive replacement.

## External media

Original media is not copied into the project by default. External references record the expected identity, including hash when available. Missing or changed media is explicit and never silently substituted.

## Time

Project time uses rational values rather than floating-point seconds as the canonical representation. Interchange adapters may convert to frame, sample or nanosecond domains with explicit rounding rules.
