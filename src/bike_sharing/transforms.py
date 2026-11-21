"""Candidate response transformations and count-scale back-transformation."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from bike_sharing.config import CANDIDATE_SCALES


def estimate_boxcox_lambda(counts: pd.Series | np.ndarray) -> float:
    """Estimate the Box--Cox exponent from strictly positive training counts."""
    values = np.asarray(counts, dtype=float)
    if np.any(values <= 0):
        raise ValueError("Box--Cox requires strictly positive counts.")
    return float(stats.boxcox(values)[1])


def add_candidate_responses(
    data: pd.DataFrame, lam: float | None = None
) -> tuple[pd.DataFrame, float]:
    """Add raw, square-root, log and Box--Cox response columns."""
    result = data.copy()
    if lam is None:
        lam = estimate_boxcox_lambda(result["cnt"])
    counts = result["cnt"].astype(float)
    result["sqrt_cnt"] = np.sqrt(counts)
    result["log1p_cnt"] = np.log1p(counts)
    result["boxcox_cnt"] = (counts**lam - 1) / lam
    return result, lam


def inverse_transform(value: np.ndarray, target: str, lam: float) -> np.ndarray:
    """Map one transformed response value back to the original count scale."""
    if target == "cnt":
        return value
    if target == "sqrt_cnt":
        return np.clip(value, 0, None) ** 2
    if target == "log1p_cnt":
        return np.exp(value) - 1
    if target == "boxcox_cnt":
        return np.clip(1 + lam * value, 1e-12, None) ** (1 / lam)
    raise ValueError(f"Unknown response scale: {target}")


def backtransform(
    target: str,
    fitted: np.ndarray | pd.Series,
    residuals: np.ndarray | pd.Series,
    *,
    lam: float | None = None,
    batch_size: int = 1000,
) -> np.ndarray:
    """Apply Duan's smearing correction on the selected response scale."""
    fitted_array = np.asarray(fitted, dtype=float)
    residual_array = np.asarray(residuals, dtype=float)
    if target not in CANDIDATE_SCALES:
        raise ValueError(f"Unknown response scale: {target}")
    if target == "cnt":
        return np.clip(fitted_array, 0, None)
    if target == "log1p_cnt":
        factor = float(np.mean(np.exp(residual_array)))
        return np.clip(np.exp(fitted_array) * factor - 1, 0, None)
    if lam is None:
        raise ValueError("Square-root and Box--Cox back-transforms require lambda.")

    output = np.empty_like(fitted_array)
    for start in range(0, len(fitted_array), batch_size):
        stop = start + batch_size
        simulated = fitted_array[start:stop, None] + residual_array[None, :]
        output[start:stop] = np.mean(inverse_transform(simulated, target, lam), axis=1)
    return np.clip(output, 0, None)
