# MPOP implementation status — v0.1

Status: initial typed data model and unit tests added. This is an implementation scaffold, not a validated perception model.

## Implemented

- `StimulusExposure` stores ordered exposure intervals using MyPro's exact rational `TimeRange`.
- Exposure duration, longest continuous interval and presentation count are derived from the recorded intervals.
- `ParticipantOutcome` keeps task-specific responses separate from source-media observations and requires an explicit delay for memory tasks.
- `ThresholdEstimate` stores a task-specific estimate and exact rational uncertainty bounds; invalid bounds are rejected.
- Unit tests cover rational duration arithmetic, ordering validation, memory delay requirements and threshold serialization.

## Not yet implemented

- Media decoder / frame-level object tracking and annotation UI.
- Psychometric fitting, calibration, confidence intervals from participant data, and goodness-of-fit diagnostics.
- Human-subject experiment execution, consent workflows, ethics review and privacy storage.
- End-to-end reproducibility tests against real video assets.

## Interpretation rule

Exposure duration is a property of the annotated asset. Detection, recognition, memory and behavior require separate measurements. No universal millisecond threshold is inferred.