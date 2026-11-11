"""Model formulas, fitting helpers, and prediction metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error

EXPLANATORY_FORMULAS = {
    "M0_main_effects": (
        "{target} ~ C(hr) + C(workingday) + C(weather_group) + C(season) "
        "+ temp + hum + windspeed + C(yr)"
    ),
    "M1_workingday_hour": (
        "{target} ~ C(hr) * C(workingday) + C(weather_group) + C(season) "
        "+ temp + hum + windspeed + C(yr)"
    ),
    "M2_weather_hour": (
        "{target} ~ C(hr) * C(workingday) + C(weather_group) * C(hr) + C(season) "
        "+ temp + hum + windspeed + C(yr)"
    ),
    "M3_season_hour": (
        "{target} ~ C(hr) * C(workingday) + C(weather_group) * C(hr) "
        "+ C(season) * C(hr) + temp + hum + windspeed + C(yr)"
    ),
    "M4_temperature_curve": (
        "{target} ~ C(hr) * C(workingday) + C(weather_group) * C(hr) "
        "+ C(season) * C(hr) + temp + I(temp ** 2) + hum + windspeed + C(yr)"
    ),
}

PREDICTIVE_FORMULAS = {
    "P0_main_effects": (
        "log1p_cnt ~ C(hr) + C(workingday) + C(weather_group) + C(season) "
        "+ temp + I(temp ** 2) + hum + windspeed + time_index_days"
    ),
    "P1_workingday_hour": (
        "log1p_cnt ~ C(hr) * C(workingday) + C(weather_group) + C(season) "
        "+ temp + I(temp ** 2) + hum + windspeed + time_index_days"
    ),
    "P2_weather_hour": (
        "log1p_cnt ~ C(hr) * C(workingday) + C(weather_group) * C(hr) + C(season) "
        "+ temp + I(temp ** 2) + hum + windspeed + time_index_days"
    ),
}


def fit_explanatory_models(data: pd.DataFrame, target: str) -> dict[str, object]:
    """Fit the prespecified hierarchy of explanatory OLS models."""
    return {
        name: smf.ols(formula.format(target=target), data=data).fit()
        for name, formula in EXPLANATORY_FORMULAS.items()
    }


def fit_predictive_model(formula: str, training_data: pd.DataFrame) -> object:
    """Fit one log-response OLS predictive model."""
    return smf.ols(formula, data=training_data).fit()


def predict_count_with_smearing(model: object, data: pd.DataFrame) -> np.ndarray:
    """Back-transform log predictions with Duan's smearing correction."""
    predicted_log = np.asarray(model.predict(data))
    smearing_factor = float(np.mean(np.exp(model.resid)))
    return np.clip(np.exp(predicted_log) * smearing_factor - 1, 0, None)


def prediction_metrics(observed: pd.Series | np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    """Compute metrics on the original count scale."""
    observed_array = np.asarray(observed)
    return {
        "mae": float(mean_absolute_error(observed_array, predicted)),
        "rmse": float(root_mean_squared_error(observed_array, predicted)),
        "r2": float(r2_score(observed_array, predicted)),
        "rmsle": float(np.sqrt(np.mean((np.log1p(predicted) - np.log1p(observed_array)) ** 2))),
    }
