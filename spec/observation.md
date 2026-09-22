# Observation Schema

An Observation is a versioned, provenance-bearing representation of something an analyzer measured or detected.

Required conceptual fields:

- `id`: stable observation identifier.
- `type`: observation type.
- `asset_id`: source asset.
- `value`: measured value or structured payload.
- `unit`: optional measurement unit.
- `confidence`: analyzer confidence in the reported observation.
- `uncertainty`: uncertainty representation; its semantics are analyzer-defined.
- `status`: `observed`, `not_analyzed`, `failed`, or `unknown`.
- `validity`: optional temporal validity interval.
- `provenance_id`: provenance record identifying how the observation was produced.
- `schema_version`: observation schema version.

An analyzer must never silently convert `not_analyzed` or `failed` into a negative observation.

## Analyzer identity

Every produced observation records:

- analyzer id;
- analyzer version;
- code hash;
- configuration hash;
- input artifact hashes;
- execution environment when reproducibility requires it.

## Uncertainty

MyPro does not impose one universal uncertainty model. An analyzer declares the semantics of its uncertainty field and the aggregation rules that consume it.
