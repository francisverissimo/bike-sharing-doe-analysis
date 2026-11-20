"""Single regression formula, fitting helper, and test-set metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error

MODEL_FORMULA = (
    "{target} ~ C(hr) * C(workingday) + C(weather_group) + C(season) "
    "+ temp + hum + windspeed + C(yr)"
)


def model_formula(target: str = "log1p_cnt") -> str:
    """Return the single regression formula for the requested response scale."""
    return MODEL_FORMULA.format(target=target)


def fit_model(data: pd.DataFrame, target: str = "log1p_cnt") -> object:
    """Fit the prespecified OLS model."""
    return smf.ols(model_formula(target), data=data).fit()


def predict_count_with_smearing(model: object, data: pd.DataFrame) -> np.ndarray:
    """Back-transform log predictions to counts with Duan's smearing correction."""
    predicted_log = np.asarray(model.predict(data))
    smearing_factor = float(np.mean(np.exp(model.resid)))
    return np.clip(np.exp(predicted_log) * smearing_factor - 1, 0, None)


def prediction_metrics(observed: pd.Series | np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    """Compute MAE, RMSE, and out-of-sample R-squared on the count scale."""
    observed_array = np.asarray(observed)
    return {
        "mae": float(mean_absolute_error(observed_array, predicted)),
        "rmse": float(root_mean_squared_error(observed_array, predicted)),
        "r2": float(r2_score(observed_array, predicted)),
    }
