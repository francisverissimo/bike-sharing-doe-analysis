"""Statistical summaries and diagnostics shared across analysis scripts."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.stattools import durbin_watson, jarque_bera


def mean_confidence_interval(
    values: pd.Series, confidence: float = 0.95
) -> tuple[float, float, float]:
    """Return mean and a t-based confidence interval."""
    clean = values.dropna().astype(float)
    mean = float(clean.mean())
    standard_error = float(stats.sem(clean))
    margin = float(stats.t.ppf((1 + confidence) / 2, len(clean) - 1) * standard_error)
    return mean, mean - margin, mean + margin


def grouped_summary(data: pd.DataFrame, group: str, response: str = "cnt") -> pd.DataFrame:
    """Summarize a response by factor level, including 95% confidence intervals."""
    rows: list[dict[str, float | int | str]] = []
    for level, values in data.groupby(group, observed=True)[response]:
        mean, lower, upper = mean_confidence_interval(values)
        rows.append(
            {
                group: str(level),
                "n": int(values.count()),
                "mean": mean,
                "median": float(values.median()),
                "std": float(values.std()),
                "ci95_low": lower,
                "ci95_high": upper,
            }
        )
    return pd.DataFrame(rows)


def add_partial_eta_squared(anova_table: pd.DataFrame) -> pd.DataFrame:
    """Add partial eta-squared to a type-II ANOVA table."""
    result = anova_table.copy()
    residual_ss = float(result.loc["Residual", "sum_sq"])
    result["partial_eta_sq"] = result["sum_sq"] / (result["sum_sq"] + residual_ss)
    result.loc["Residual", "partial_eta_sq"] = np.nan
    return result


def nested_model_table(models: dict[str, object]) -> pd.DataFrame:
    """Compare ordered nested statsmodels OLS results."""
    names = list(models)
    comparison = anova_lm(*(models[name] for name in names))
    comparison.insert(0, "model", names)
    return comparison.reset_index(drop=True)


def residual_diagnostics(model: object, label: str) -> dict[str, float | str]:
    """Calculate a concise set of OLS residual diagnostics."""
    residuals = np.asarray(model.resid)
    jb_stat, jb_pvalue, skew, kurtosis = jarque_bera(residuals)
    bp_stat, bp_pvalue, _, _ = het_breuschpagan(residuals, model.model.exog)
    sample = residuals[np.linspace(0, len(residuals) - 1, min(5_000, len(residuals)), dtype=int)]
    shapiro_stat, shapiro_pvalue = stats.shapiro(sample)
    return {
        "model": label,
        "n": len(residuals),
        "residual_std": float(np.std(residuals, ddof=1)),
        "residual_skew": float(skew),
        "residual_kurtosis": float(kurtosis),
        "jarque_bera": float(jb_stat),
        "jarque_bera_p": float(jb_pvalue),
        "shapiro_w_5000": float(shapiro_stat),
        "shapiro_p_5000": float(shapiro_pvalue),
        "breusch_pagan": float(bp_stat),
        "breusch_pagan_p": float(bp_pvalue),
        "durbin_watson": float(durbin_watson(residuals)),
    }
