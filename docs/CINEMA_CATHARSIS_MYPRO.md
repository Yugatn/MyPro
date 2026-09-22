# Cinema Catharsis as a MyPro domain module

Cinema Catharsis is a domain module that consumes the same canonical content, fragments, observations and provenance used by MyPro's editor and social platform.

## Data flow

For stored media:

source media, probe, observations, Cinema Catharsis classification, measurements, uncertainty, report

For live sources:

authorized live source, ingest, rolling buffer, observations, candidate fragments, Cinema Catharsis measurements

MyPro Core remains responsible for identity, time, provenance, project state and authorization. Cinema Catharsis supplies domain formulas and descriptive interpretation.

## Reuse of one observation

A single observation can support multiple views without being duplicated:

- a fragment in the Viewer-Editor;
- a timeline marker;
- a montage candidate;
- a social discussion anchor;
- a Cinema Catharsis metric;
- a research export.

The observation retains its analyzer identity, version, source reference and uncertainty.

## No automatic psychological conclusion

A category occurrence can be measured. It cannot by itself establish:

- that a viewer noticed it;
- that a viewer experienced a particular emotion;
- that a viewer changed an attitude;
- that a viewer suffered harm;
- that the content caused a later behavior.

Those questions belong to separate exposure, response and audience-study layers.

## Versioning

Every formula set is versioned with the project schema and analyzer metadata. A report identifies the Cinema Catharsis methodology version, ontology version, analyzer or coder version, source content hash, analyzed time range, missing or dropped ranges, formula configuration and uncertainty representation.

This makes reports reproducible when the same source artifacts remain available.

## Connected projects

Cinema Catharsis defines a formal content-analysis methodology.

MyPro provides the open technical substrate that stores, analyzes, edits, publishes and discusses the same evidence.

Eugene Messenger can provide communication for discussions attached to content, fragments and time ranges without changing the evidentiary status of the underlying observation.