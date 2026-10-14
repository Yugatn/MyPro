# Psychometric utility status — prototype

`core/analysis/psychometric.py` now provides a dependency-free logistic probability curve, its inverse for a declared target probability, and a basic empirical accuracy helper.

## Scope

- The curve is a declared model, not a fit to human-subject data.
- `duration_at_probability` returns a model-implied duration only when the target lies strictly between the model's lower and upper asymptotes.
- This utility does not estimate parameters, confidence intervals, goodness of fit, or population variability.
- A duration derived from assumed parameters must not be reported as an empirical or universal perception threshold.

Tests are authored in `tests/test_psychometric.py`. They still require execution in the repository's supported Python environment before the prototype can be described as test-passing.

## v0.2 — parameter-fitting prototype

`core/analysis/psychometric_fit.py` adds binomial negative log-likelihood fitting for the midpoint and positive slope using deterministic coordinate search. Guess and lapse rates are fixed inputs. The routine rejects constant response-rate patterns and requires at least three distinct exposure durations. It returns a point estimate and convergence diagnostics only; it does **not** calculate confidence intervals or account for participant-level random effects. Tests are in `tests/test_psychometric_fit.py` and have been authored but not run in this environment.


## Synthetic smoke check

`scripts/validate_psychometric_synthetic.py` defines a deterministic synthetic-data smoke check with known curve parameters. Run it from the repository root using `python -m scripts.validate_psychometric_synthetic`. It checks only basic recovery on generated data and is not evidence of validity for human perception. The script has been authored but not executed in the repository environment.
