"""Global parameter estimation and batch-aware bootstrap uncertainty."""

from dataclasses import asdict

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

from .data import validate_dataset
from .model import BatchCondition, KineticParameters, cumulative_methane

PARAMETER_NAMES = tuple(asdict(KineticParameters()).keys())
LOWER = np.array([50, 1, 0, -1, -1, -1, -1, 1.01], dtype=float)
UPPER = np.array([1000, 100, 15, 1, 0.5, 1, 0.5, 4], dtype=float)

# Above this absolute pairwise correlation, two parameters are considered
# practically confounded: the data cannot tell their individual values apart,
# only some combination of them (Bates & Watts 1988, ch. 3 on curvature and
# near-collinearity in nonlinear least squares).
IDENTIFIABILITY_CORRELATION_THRESHOLD = 0.95


def _unpack(values: np.ndarray) -> KineticParameters:
    return KineticParameters(**dict(zip(PARAMETER_NAMES, values, strict=True)))


def predict_frame(frame: pd.DataFrame, parameters: KineticParameters) -> np.ndarray:
    """Predict each observation while preserving input row order."""

    prediction = np.empty(len(frame), dtype=float)
    for (_, dose, temperature), indices in frame.groupby(
        ["batch_id", "dose_g_l", "temperature_c"], sort=False
    ).groups.items():
        positions = frame.index.get_indexer(indices)
        subset = frame.loc[indices]
        prediction[positions] = cumulative_methane(
            subset["time_days"].to_numpy(),
            BatchCondition(float(dose), float(temperature)),
            parameters,
        )
    return prediction


def parameter_covariance(solution, n_observations: int) -> np.ndarray:
    """Approximate the parameter covariance matrix at a least_squares solution.

    Uses the standard nonlinear-least-squares approximation
    ``cov = residual_variance * pinv(J^T J)`` (Bates & Watts 1988), where ``J``
    is the Jacobian of the residuals at the solution. A pseudo-inverse is used
    because near-confounded parameters make ``J^T J`` close to singular; that
    near-singularity is itself the identifiability signal callers should read
    from the resulting correlations, not an error to hide.
    """

    jacobian = solution.jac
    n_params = jacobian.shape[1]
    degrees_of_freedom = max(n_observations - n_params, 1)
    residual_variance = float(np.sum(solution.fun**2)) / degrees_of_freedom
    return residual_variance * np.linalg.pinv(jacobian.T @ jacobian)


def parameter_correlation_matrix(covariance: np.ndarray) -> pd.DataFrame:
    """Turn a parameter covariance matrix into a labelled correlation matrix."""

    standard_error = np.sqrt(np.clip(np.diag(covariance), 0, None))
    outer = np.outer(standard_error, standard_error)
    with np.errstate(invalid="ignore", divide="ignore"):
        correlation = np.where(outer > 0, covariance / outer, np.nan)
    return pd.DataFrame(correlation, index=PARAMETER_NAMES, columns=PARAMETER_NAMES)


def _identifiability_metrics(solution, n_observations: int) -> dict[str, float]:
    covariance = parameter_covariance(solution, n_observations)
    correlation = parameter_correlation_matrix(covariance).to_numpy()
    n_params = correlation.shape[0]
    off_diagonal = correlation[~np.eye(n_params, dtype=bool)]
    off_diagonal = off_diagonal[np.isfinite(off_diagonal)]
    max_correlation = float(np.max(np.abs(off_diagonal))) if off_diagonal.size else float("nan")
    gram = solution.jac.T @ solution.jac
    condition_number = float(np.linalg.cond(gram)) if np.all(np.isfinite(gram)) else float("inf")
    return {
        "max_parameter_correlation": max_correlation,
        "parameter_gram_condition_number": condition_number,
    }


def fit_global(frame: pd.DataFrame) -> tuple[KineticParameters, dict[str, float]]:
    """Fit all batch conditions simultaneously and return diagnostic metrics.

    ``max_parameter_correlation`` and ``parameter_gram_condition_number`` in the
    returned metrics are practical-identifiability diagnostics, not goodness of
    fit: a high correlation (beyond ``IDENTIFIABILITY_CORRELATION_THRESHOLD``)
    or condition number means the data cannot separate two or more of the
    eight kinetic parameters, even when RMSE/R-squared look good.
    """

    frame = frame.reset_index(drop=True).copy()
    validate_dataset(frame)
    observed = frame["methane_ml_g_vs"].to_numpy(dtype=float)

    def residual(values: np.ndarray) -> np.ndarray:
        return predict_frame(frame, _unpack(values)) - observed

    initial = np.array(list(asdict(KineticParameters()).values()), dtype=float)
    solution = least_squares(residual, initial, bounds=(LOWER, UPPER), loss="soft_l1")
    parameters = _unpack(solution.x)
    fitted = predict_frame(frame, parameters)
    errors = observed - fitted
    ss_total = float(np.sum((observed - observed.mean()) ** 2))
    metrics = {
        "rmse_ml_g_vs": float(np.sqrt(np.mean(errors**2))),
        "mae_ml_g_vs": float(np.mean(np.abs(errors))),
        "r_squared": float(1 - np.sum(errors**2) / ss_total),
        "n_observations": float(len(frame)),
    }
    metrics.update(_identifiability_metrics(solution, len(observed)))
    return parameters, metrics


def bootstrap_parameters(
    frame: pd.DataFrame, iterations: int = 100, seed: int = 27
) -> pd.DataFrame:
    """Estimate uncertainty by resampling residuals independently within batches."""

    if iterations < 1:
        raise ValueError("Bootstrap iterations must be positive")
    frame = frame.reset_index(drop=True).copy()
    baseline, _ = fit_global(frame)
    fitted = predict_frame(frame, baseline)
    residuals = frame["methane_ml_g_vs"].to_numpy() - fitted
    rng = np.random.default_rng(seed)
    samples: list[dict[str, float]] = []
    groups = frame.groupby("batch_id").indices
    for _ in range(iterations):
        simulated = frame.copy()
        response = fitted.copy()
        for indices in groups.values():
            response[indices] += rng.choice(residuals[indices], size=len(indices), replace=True)
        simulated["methane_ml_g_vs"] = np.clip(response, 0, None)
        try:
            estimate, _ = fit_global(simulated)
            samples.append(asdict(estimate))
        except (ValueError, RuntimeError):
            continue
    return pd.DataFrame(samples)

