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


def fit_global(frame: pd.DataFrame) -> tuple[KineticParameters, dict[str, float]]:
    """Fit all batch conditions simultaneously and return diagnostic metrics."""

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

