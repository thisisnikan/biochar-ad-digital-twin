"""Transparent benchmarking of empirical BMP kinetic models.

The models in this module are descriptive. Model selection metrics help avoid
choosing a curve solely because it reports a high coefficient of determination.
"""

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from scipy.optimize import least_squares


Curve = Callable[..., NDArray[np.float64]]


@dataclass(frozen=True)
class ModelSpec:
    name: str
    curve: Curve
    parameter_names: tuple[str, ...]
    lower: tuple[float, ...]
    upper: tuple[float, ...]


def first_order(
    time: NDArray[np.float64], potential: float, rate_constant: float
) -> NDArray[np.float64]:
    """First-order methane formation without an explicit lag phase."""

    return potential * (1.0 - np.exp(-rate_constant * time))


def modified_gompertz(
    time: NDArray[np.float64], potential: float, max_rate: float, lag_days: float
) -> NDArray[np.float64]:
    """Modified Gompertz cumulative methane curve."""

    exponent = (np.e * max_rate / potential) * (lag_days - time) + 1.0
    return potential * np.exp(-np.exp(np.clip(exponent, -50.0, 50.0)))


def modified_logistic(
    time: NDArray[np.float64], potential: float, max_rate: float, lag_days: float
) -> NDArray[np.float64]:
    """Modified logistic cumulative methane curve."""

    exponent = (4.0 * max_rate / potential) * (lag_days - time) + 2.0
    return potential / (1.0 + np.exp(np.clip(exponent, -50.0, 50.0)))


def cone(
    time: NDArray[np.float64], potential: float, rate_constant: float, shape: float
) -> NDArray[np.float64]:
    """Cone model written in a numerically stable cumulative form."""

    scaled = np.power(np.maximum(rate_constant * time, 0.0), shape)
    return potential * scaled / (1.0 + scaled)


MODEL_SPECS = (
    ModelSpec(
        "first_order",
        first_order,
        ("potential", "rate_constant"),
        (1.0, 1e-5),
        (2000.0, 10.0),
    ),
    ModelSpec(
        "modified_gompertz",
        modified_gompertz,
        ("potential", "max_rate", "lag_days"),
        (1.0, 1e-4, 0.0),
        (2000.0, 500.0, 30.0),
    ),
    ModelSpec(
        "modified_logistic",
        modified_logistic,
        ("potential", "max_rate", "lag_days"),
        (1.0, 1e-4, 0.0),
        (2000.0, 500.0, 30.0),
    ),
    ModelSpec(
        "cone",
        cone,
        ("potential", "rate_constant", "shape"),
        (1.0, 1e-5, 0.05),
        (2000.0, 10.0, 10.0),
    ),
)


def _initial_values(
    spec: ModelSpec, time: NDArray[np.float64], observed: NDArray[np.float64]
) -> NDArray[np.float64]:
    potential = max(float(observed.max()) * 1.05, 1.0)
    positive_time = np.maximum(time, 1e-6)
    rate_constant = max(1.0 / max(float(np.median(positive_time)), 1.0), 0.01)
    if len(time) > 1:
        slopes = np.diff(observed) / np.maximum(np.diff(time), 1e-6)
        max_rate = max(float(np.max(slopes)), 0.1)
    else:
        max_rate = 1.0
    threshold = 0.05 * max(float(observed.max()), 1.0)
    active = time[observed >= threshold]
    lag = max(float(active[0]) - 1.0, 0.0) if active.size else 0.0
    if spec.name == "first_order":
        return np.array([potential, rate_constant])
    if spec.name == "cone":
        return np.array([potential, rate_constant, 2.0])
    return np.array([potential, max_rate, lag])


def fit_model(
    spec: ModelSpec, time: NDArray[np.float64], observed: NDArray[np.float64]
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Estimate one model using ordinary nonlinear least squares."""

    initial = _initial_values(spec, time, observed)
    solution = least_squares(
        lambda values: spec.curve(time, *values) - observed,
        initial,
        bounds=(np.asarray(spec.lower), np.asarray(spec.upper)),
        loss="linear",
    )
    return solution.x, spec.curve(time, *solution.x)


def _metrics(
    observed: NDArray[np.float64], predicted: NDArray[np.float64], parameters: int
) -> dict[str, float]:
    residual = observed - predicted
    observations = len(observed)
    rss = max(float(np.sum(residual**2)), np.finfo(float).tiny)
    total = float(np.sum((observed - observed.mean()) ** 2))
    aic = observations * np.log(rss / observations) + 2 * parameters
    correction = (
        2 * parameters * (parameters + 1) / (observations - parameters - 1)
        if observations > parameters + 1
        else np.inf
    )
    return {
        "rmse": float(np.sqrt(rss / observations)),
        "mae": float(np.mean(np.abs(residual))),
        "r_squared": float(1 - rss / total) if total > 0 else np.nan,
        "aicc": float(aic + correction),
        "bic": float(
            observations * np.log(rss / observations) + parameters * np.log(observations)
        ),
    }


def _late_holdout_rmse(
    spec: ModelSpec,
    time: NDArray[np.float64],
    observed: NDArray[np.float64],
    fraction: float = 0.25,
) -> float:
    split = max(int(np.floor(len(time) * (1.0 - fraction))), len(spec.parameter_names) + 2)
    if split >= len(time):
        return np.nan
    parameters, _ = fit_model(spec, time[:split], observed[:split])
    prediction = spec.curve(time[split:], *parameters)
    return float(np.sqrt(np.mean((observed[split:] - prediction) ** 2)))


def compare_models(frame: pd.DataFrame) -> pd.DataFrame:
    """Fit all benchmark models independently to each batch condition."""

    required = {"batch_id", "time_days", "dose_g_l", "temperature_c", "methane_ml_g_vs"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")

    rows: list[dict[str, float | str]] = []
    grouped = frame.sort_values("time_days").groupby(
        ["batch_id", "dose_g_l", "temperature_c"], sort=False
    )
    for (batch_id, dose, temperature), batch in grouped:
        time = batch["time_days"].to_numpy(dtype=float)
        observed = batch["methane_ml_g_vs"].to_numpy(dtype=float)
        if len(time) < 6:
            raise ValueError(f"Batch {batch_id} needs at least six observations")
        for spec in MODEL_SPECS:
            parameters, predicted = fit_model(spec, time, observed)
            result: dict[str, float | str] = {
                "batch_id": str(batch_id),
                "dose_g_l": float(dose),
                "temperature_c": float(temperature),
                "model": spec.name,
                "late_holdout_rmse": _late_holdout_rmse(spec, time, observed),
            }
            result.update(_metrics(observed, predicted, len(parameters)))
            named_parameters = zip(spec.parameter_names, parameters, strict=True)
            result.update({name: float(value) for name, value in named_parameters})
            rows.append(result)

    comparison = pd.DataFrame(rows)
    comparison["delta_aicc"] = comparison.groupby("batch_id")["aicc"].transform(
        lambda values: values - values.min()
    )
    comparison["aicc_rank"] = comparison.groupby("batch_id")["aicc"].rank(method="min")
    return comparison.sort_values(["batch_id", "aicc_rank", "model"]).reset_index(drop=True)
