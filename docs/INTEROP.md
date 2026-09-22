# Interoperability

MyPro keeps its canonical project and evidence models independent from external tools.

## FFmpeg and FFprobe

FFprobe is the initial technical media probe. Its structured output can populate MediaManifest fields. FFmpeg is an external processing backend, not the canonical project model.

## OpenTimelineIO

OpenTimelineIO is an interchange boundary for editorial timelines. OTIO is not the hidden source of truth for MyPro projects.

## C2PA / Content Credentials

C2PA is an interoperability target for content provenance and credentials. MyPro provenance can be exported into compatible evidence where the semantics match.

## W3C PROV

The provenance model is designed so that relevant entities, activities and derivations can be mapped to W3C PROV concepts.

## MLT

MLT may be used as a future render/media backend. Its data model must remain an integration boundary.

## EDL, XML and AAF

These formats are export/interchange targets. Importers and exporters must declare loss, rounding and unsupported-feature behavior rather than silently dropping semantics.

## Licensing

Open-source synthesis means using compatible dependencies and architectural ideas, not copying source code across incompatible licenses. GPL-licensed reference applications are treated as workflow references or isolated integrations unless a future licensing decision explicitly permits otherwise.
