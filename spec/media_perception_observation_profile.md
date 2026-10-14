# Media Perception Observation Profile (MPOP) v0.1

**Status:** proposal for implementation. This document defines a schema profile; it does not claim that a perception-threshold analyzer or a human-subject experiment has already been implemented.

## Purpose

Provide a reproducible way to represent temporal media observations and, separately, measured participant outcomes. MPOP builds on MyPro's versioned Observation, rational Time Model, provenance records, and Analysis DAG.

## Separation of evidence layers

- **Media observation:** properties measured from a source asset (visible intervals, count, size, contrast, occlusion, audio/visual context).
- **Participant response:** an outcome recorded in a declared task (detection, identification, confidence, recall, recognition, source memory, delayed retention, or declared physiological measure).
- **Interpretation:** an explanation derived from observations, with alternatives and limitations.
- **Claim about effect:** requires a defined design and evidence appropriate to the causal claim.

A media observation must never be silently promoted to a participant response or a causal effect.

## Proposed record families

### StimulusExposure

- asset_id, asset_hash, source_version
- timebase_id
- intervals: exact rational half-open intervals [start, end)
- total_visible_duration
- longest_contiguous_duration
- presentation_count
- inter_presentation_intervals
- visibility_method, annotator_or_analyzer_id
- configuration_hash, provenance_id
- confidence, uncertainty, status

Durations must be derived from the declared timebase. Do not infer human perception from these fields.

### StimulusFeatures

- object_class (e.g. cigarette pack, bottle, logo; avoid asserting brand when uncertain)
- relative_screen_area, screen_position
- contrast_method, contrast_value where measurable
- motion, occlusion, sharpness
- visual_context, audio_context, shot_context
- feature_extraction_method, provenance_id, uncertainty and status

Features are descriptive measurements, not a universal salience score unless a score is explicitly defined and validated.

### ParticipantOutcome

- participant_id: pseudonymous study-local identifier; identity data stored separately under appropriate safeguards
- study_id, trial_id, condition_id
- task_type: detection | identification | confidence | free_recall | recognition | source_memory | delayed_recall | delayed_recognition | physiological_measure | attitude | behavior
- response, correctness if defined, reaction_time if measured
- measurement_device_or_instrument, protocol_version
- baseline_and_artifact_rules for physiological measurements
- assessment_delay, trial_order, exposure_duration
- consent_status, ethics/governance reference where applicable
- provenance_id, missingness reason, uncertainty and status

Do not store direct identifiers in this record. Physiological measurements require a declared signal, units, sampling method, preprocessing, baseline, artifact handling, and interpretation boundary.

### ThresholdEstimate

- study_id, task_type, stimulus_definition, population_definition
- criterion_definition fixed before analysis
- estimation_method, model_version, data_hash
- estimate, unit, uncertainty_interval
- fit_diagnostics, exclusion_summary, limitations
- replication_status, provenance_id

A threshold is conditional on the task, stimulus, sample, viewing conditions and criterion. It must not be labeled a universal minimum duration for human perception or memory.

## Invariants

1. I_exposure_is_not_perception: exposure records alone cannot support claims that a participant detected, recognized or remembered the stimulus.
2. I_task_specific_threshold: every threshold identifies its task, criterion, sample, stimulus and conditions.
3. I_timebase_preserved: interval conversion preserves precision to the declared timebase resolution.
4. I_provenance_complete: every derived estimate identifies inputs, analyzer/model version, configuration and data hashes.
5. I_missing_not_negative: missing, failed or untested measurements are not encoded as a negative result.
6. I_memory_delay_explicit: memory outcomes specify test type and delay.
7. I_physio_not_mind_reading: physiological signals are not direct evidence of a specific thought, intention or emotion without additional validated evidence.
8. I_no_silent_causal_claim: causal effect claims require an appropriate design and declared assumptions.
9. I_privacy_minimization: participant records use pseudonymous study-local identifiers and minimize sensitive data.
10. I_human_review: automated annotations remain reviewable; disagreements and corrections are retained in provenance.

## Analysis DAG

A candidate pipeline is:

MediaAsset -> ExposureAnnotation -> FeatureExtraction -> HumanReviewedStimulusSet

and, for a separate study:

StudyProtocol + StimulusSet + ParticipantResponses -> QualityChecks -> TaskSpecificModel -> ThresholdEstimate -> HumanReviewedFinding

These are conceptual dependencies, not a claim that implementation exists. Each node must declare version, input hashes, configuration hash, provenance and invalidation rules under the existing Analysis DAG specification.

## Evaluation and validation

Before calling an implementation validated, test at least:
- exact interval arithmetic, boundary and frame-rate cases;
- variable-frame-rate media and timebase conversion;
- repeated, overlapping and occluded object intervals;
- inter-annotator agreement and adjudication;
- simulated psychometric curves with known parameters;
- missing/failed trials and participant exclusions;
- calibration and uncertainty coverage;
- reproducible reruns from pinned inputs and configuration;
- separation of stimulus-only findings from participant outcomes;
- privacy and consent enforcement.

## Non-goals

MPOP does not infer a universal millisecond threshold, diagnose individual viewers, read mental states from physiological signals, prove product placement, or establish a causal media effect from exposure duration alone.