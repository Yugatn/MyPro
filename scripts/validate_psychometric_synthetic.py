"""Deterministic synthetic smoke check for the psychometric fitting prototype.

Run from repository root with:
    python -m scripts.validate_psychometric_synthetic

This checks code behavior against generated data only; it is not empirical validation.
"""

from core.analysis.psychometric import LogisticPsychometricModel
from core.analysis.psychometric_fit import PsychometricBin, fit_logistic_mle

def main() -> None:
    expected = LogisticPsychometricModel(midpoint_seconds=0.2, slope_per_second=25.0)
    durations = (0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35)
    bins = tuple(
        PsychometricBin(duration, round(expected.probability(duration) * 100), 100)
        for duration in durations
    )
    fitted = fit_logistic_mle(bins, max_iterations=1000)
    print(f"converged={fitted.converged}")
    print(f"iterations={fitted.iterations}")
    print(f"midpoint_seconds={fitted.model.midpoint_seconds:.6f}")
    print(f"slope_per_second={fitted.model.slope_per_second:.6f}")
    print(f"negative_log_likelihood={fitted.negative_log_likelihood:.6f}")
    if not fitted.converged:
        raise SystemExit("synthetic smoke check failed: optimizer did not converge")
    if abs(fitted.model.midpoint_seconds - expected.midpoint_seconds) > 0.04:
        raise SystemExit("synthetic smoke check failed: midpoint outside tolerance")

if __name__ == "__main__":
    main()