"""Progressive M0--M4 model sequence, fitting helpers, and test-set metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error

from bike_sharing.transforms import backtransform

BASE_TERMS = "C(hr) + C(workingday) + C(weather_group) + C(season) + temp + hum + windspeed"
MODEL_SEQUENCE = {
    "M0": "{target} ~ " + BASE_TERMS,
    "M1": (
        "{target} ~ C(hr) * C(workingday) + C(weather_group) + C(season) "
        "+ temp + hum + windspeed"
    ),
    "M2": (
        "{target} ~ C(hr) * C(workingday) + C(hr) * C(weather_group) "
        "+ C(hr) * C(season) + temp + hum + windspeed"
    ),
    "M3": (
        "{target} ~ C(hr) * C(workingday) + C(hr) * C(weather_group) "
        "+ C(hr) * C(season) + temp + I(temp**2) + hum + windspeed"
    ),
}
MODEL_FORMULA = MODEL_SEQUENCE["M1"]
TERMS_ADDED = {
    "M0": "Main effects",
    "M1": "+ hour x working day",
    "M2": "+ hour x weather, hour x season",
    "M3": "+ quadratic temperature",
}
MODEL_ORDER = tuple(MODEL_SEQUENCE)


def model_formula(target: str = "log1p_cnt", model: str = "M1") -> str:
    """Return the formula for one candidate in the progressive model sequence."""
    if model not in MODEL_SEQUENCE:
        raise ValueError(f"Unknown model: {model}")
    return MODEL_SEQUENCE[model].format(target=target)


def fit_model(data: pd.DataFrame, target: str = "log1p_cnt", model: str = "M1") -> object:
    """Fit one candidate model by ordinary least squares."""
    return smf.ols(model_formula(target, model), data=data).fit()


def fit_model_sequence(data: pd.DataFrame, target: str = "log1p_cnt") -> dict[str, object]:
    """Fit M0--M3 on the same training sample."""
    return {name: fit_model(data, target, name) for name in MODEL_ORDER}


def compare_models(fits: dict[str, object]) -> pd.DataFrame:
    """Compare nested candidate models on training fit and parsimony."""
    rows: list[dict[str, float | int | str]] = []
    previous_name: str | None = None
    for name in MODEL_ORDER:
        model = fits[name]
        row: dict[str, float | int | str] = {
            "model": name,
            "terms_added": TERMS_ADDED[name],
            "parameters": int(model.df_model + 1),
            "adjusted_r_squared": float(model.rsquared_adj),
            "aic": float(model.aic),
            "bic": float(model.bic),
        }
        if previous_name is None:
            row["f_statistic"] = np.nan
            row["f_p_value"] = np.nan
        else:
            statistic, pvalue, _ = model.compare_f_test(fits[previous_name])
            row["f_statistic"] = float(statistic)
            row["f_p_value"] = float(pvalue)
        rows.append(row)
        previous_name = name
    return pd.DataFrame(rows)


def select_model_by_bic(fits: dict[str, object]) -> str:
    """Select the candidate with the lowest training BIC; ties keep the simpler model."""
    best = min(MODEL_ORDER, key=lambda name: (fits[name].bic, MODEL_ORDER.index(name)))
    return best


def predict_count(
    model: object,
    data: pd.DataFrame,
    *,
    target: str = "log1p_cnt",
    lam: float | None = None,
) -> np.ndarray:
    """Predict counts with a scale-appropriate smearing correction."""
    return backtransform(target, model.predict(data), model.resid, lam=lam)


def predict_count_with_smearing(
    model: object,
    data: pd.DataFrame,
    *,
    target: str = "log1p_cnt",
    lam: float | None = None,
) -> np.ndarray:
    """Backward-compatible alias for :func:`predict_count`."""
    return predict_count(model, data, target=target, lam=lam)


def prediction_metrics(observed: pd.Series | np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    """Compute MAE, RMSE, and out-of-sample R-squared on the count scale."""
    observed_array = np.asarray(observed)
    return {
        "mae": float(mean_absolute_error(observed_array, predicted)),
        "rmse": float(root_mean_squared_error(observed_array, predicted)),
        "r2": float(r2_score(observed_array, predicted)),
    }
