"""Model comparison and validation utilities for BMP research workflows."""

from __future__ import annotations

from dataclasses import asdict

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

from biochar_ad_twin.fit import fit_global, predict_frame


def information_criteria(observed: np.ndarray, predicted: np.ndarray, k: int) -> dict[str, float]:
    """Return Gaussian AIC, small-sample AICc and BIC from unweighted residuals."""
    observed = np.asarray(observed, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    n = observed.size
    if n != predicted.size or n <= k + 1:
        raise ValueError("AICc requires equal vectors and n > k + 1")
    rss = float(np.sum((observed - predicted) ** 2))
    rss = max(rss, np.finfo(float).tiny)
    aic = n * np.log(rss / n) + 2 * k
    return {
        "aic": float(aic),
        "aicc": float(aic + (2 * k * (k + 1)) / (n - k - 1)),
        "bic": float(n * np.log(rss / n) + k * np.log(n)),
    }


def _fit_constant_gompertz(frame: pd.DataFrame) -> tuple[np.ndarray, int]:
    """Fit an intentionally simple condition-agnostic modified Gompertz baseline."""
    time = frame["time_days"].to_numpy(float)
    observed = frame["methane_ml_g_vs"].to_numpy(float)

    def prediction(values: np.ndarray) -> np.ndarray:
        potential, rate, lag = values
        exponent = (np.e * rate / potential) * (lag - time) + 1.0
        return potential * np.exp(-np.exp(np.clip(exponent, -50.0, 50.0)))

    solution = least_squares(
        lambda values: prediction(values) - observed,
        x0=np.array([300.0, 18.0, 2.0]),
        bounds=([1.0, 0.01, 0.0], [2000.0, 500.0, 30.0]),
        loss="linear",
    )
    return prediction(solution.x), 3


def compare_models(frame: pd.DataFrame) -> pd.DataFrame:
    """Compare the proposed global model with a parsimonious Gompertz baseline."""
    frame = frame.reset_index(drop=True)
    observed = frame["methane_ml_g_vs"].to_numpy(float)
    parameters, _ = fit_global(frame)
    candidates = {
        "global_dose_temperature": (predict_frame(frame, parameters), len(asdict(parameters))),
        "constant_gompertz": _fit_constant_gompertz(frame),
    }
    rows = []
    for name, (predicted, k) in candidates.items():
        residual = observed - predicted
        rows.append(
            {
                "model": name,
                "parameters": k,
                "rmse_ml_g_vs": float(np.sqrt(np.mean(residual**2))),
                **information_criteria(observed, predicted, k),
            }
        )
    result = pd.DataFrame(rows).sort_values("aicc").reset_index(drop=True)
    result["delta_aicc"] = result["aicc"] - result["aicc"].min()
    return result


def leave_one_batch_out(frame: pd.DataFrame) -> pd.DataFrame:
    """Estimate extrapolation error by withholding every experimental batch once."""
    rows = []
    for batch_id in frame["batch_id"].drop_duplicates():
        train = frame.loc[frame["batch_id"] != batch_id].reset_index(drop=True)
        test = frame.loc[frame["batch_id"] == batch_id].reset_index(drop=True)
        parameters, _ = fit_global(train)
        residual = test["methane_ml_g_vs"].to_numpy(float) - predict_frame(test, parameters)
        rows.append(
            {
                "held_out_batch": batch_id,
                "n_test": len(test),
                "rmse_ml_g_vs": float(np.sqrt(np.mean(residual**2))),
                "mae_ml_g_vs": float(np.mean(np.abs(residual))),
            }
        )
    return pd.DataFrame(rows)
