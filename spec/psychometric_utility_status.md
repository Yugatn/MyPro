# Psychometric utility status — prototype

`core/analysis/psychometric.py` now provides a dependency-free logistic probability curve, its inverse for a declared target probability, and a basic empirical accuracy helper.

## Scope

- The curve is a declared model, not a fit to human-subject data.
- `duration_at_probability` returns a model-implied duration only when the target lies strictly between the model's lower and upper asymptotes.
- This utility does not estimate parameters, confidence intervals, goodness of fit, or population variability.
- A duration derived from assumed parameters must not be reported as an empirical or universal perception threshold.

Tests are authored in `tests/test_psychometric.py`. They still require execution in the repository's supported Python environment before the prototype can be described as test-passing.