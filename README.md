# MyPro — Evidence Core for verifiable digital content

MyPro is an open modular platform for analysis, creation, montage, transformation and verification of digital content.

The core is an event-sourced, content-addressed model. Media, observations, montage state, proposals and decisions are designed to remain inspectable and reproducible.

## Foundation v0.4

The runnable vertical slice now includes:

- algorithm-aware content hashes with BLAKE3 and SHA-256;
- exact rational time and half-open ranges;
- hash-chained append-only event log with incomplete-tail recovery;
- atomic content-addressed snapshots;
- project creation, backup, verification and restore;
- layered multi-track Montage Model primitives;
- split, trim, move and compound operations;
- compound flattening for renderer-facing consumers;
- montage invariant validation;
- Universal Import Layer with an OTIO adapter;
- import loss, mapping and source provenance reporting;
- reusable semantic content fragments;
- Viewer-Editor interaction primitives;
- Cinema Catharsis descriptive measurement formulas;
- CLI and end-to-end demo;
- automated foundation tests.

## Cinema Catharsis

Cinema Catharsis is a connected research and measurement layer for MyPro.

MyPro stores the evidence substrate: source media, exact time ranges, observations, fragments, provenance, versions and editorial decisions. Cinema Catharsis defines a descriptive ontology and formal measurements over that evidence.

The current measurement layer covers weighted event count, category duration, screen-time share, event density, coverage, time density, repeatability, relative category distribution, union duration, normalized entropy, coding uncertainty and duration-based category co-occurrence.

The methodology keeps content, exposure, response, effect and harm separate. Content measurements do not automatically become claims about viewer psychology, audience attitude, harm or causality.

See docs/CINEMA_CATHARSIS.md and docs/CINEMA_CATHARSIS_MYPRO.md.

## Quick start

```bash
pip install -e ".[dev]"
python demo.py /tmp/mypro-demo
pytest -q
```

CLI:

```bash
mypro init /tmp/project.mypro
mypro backup /tmp/project.mypro --label morning
mypro verify /tmp/project.mypro
mypro restore /tmp/project.mypro <digest> /tmp/restored.mypro
mypro import-project timeline.otio /tmp/project.mypro
```

Import is proposal-oriented. The default import command performs a dry run and does not mutate montage state.

## Architecture

```text
MyPro
├── Media
├── Analysis
│   └── Cinema Catharsis
├── Evidence
├── Project
├── Montage
├── AI
├── Security
├── Runtime
└── Integrations
```

OpenTimelineIO is treated as interchange. The canonical MyPro model remains independent of any one editor or interchange format.

## Core invariants

- event records form a verifiable hash chain;
- incomplete final event writes can be recovered without rewriting valid history;
- snapshots are installed through temporary files and atomic replacement;
- canonical time does not use floating-point seconds;
- montage layers on one track cannot overlap;
- compound timeline references cannot form cycles;
- clip source references must resolve;
- imports report loss and mapping explicitly;
- import adapters produce evidence/proposals rather than directly changing project state;
- Cinema Catharsis metrics preserve source provenance and coding uncertainty;
- Cinema Catharsis content metrics are not silently converted into audience-effect or harm claims.

## Design boundary

AI and analyzers produce proposals. Core validation and policy are separate from execution. A proposal is not an action, and an observation is not a conclusion.

## Next implementation layer

The next production-facing slice is FFmpeg render verification, followed by the live ingest and rolling-buffer runtime, a minimal Editorial Model, Intent Model and MCP authorization boundary.

## License

MIT.
