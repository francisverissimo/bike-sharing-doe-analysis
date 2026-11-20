"""Statistical summaries and basic diagnostics shared across analysis scripts."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.diagnostic import het_breuschpagan


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


def residual_diagnostics(model: object, label: str) -> dict[str, float | str]:
    """Calculate basic residual normality and constant-variance diagnostics."""
    residuals = np.asarray(model.resid)
    sample = residuals[np.linspace(0, len(residuals) - 1, min(5_000, len(residuals)), dtype=int)]
    shapiro_stat, shapiro_pvalue = stats.shapiro(sample)
    bp_stat, bp_pvalue, _, _ = het_breuschpagan(residuals, model.model.exog)
    return {
        "scale": label,
        "n": len(residuals),
        "residual_std": float(np.std(residuals, ddof=1)),
        "shapiro_w_5000": float(shapiro_stat),
        "shapiro_p_5000": float(shapiro_pvalue),
        "breusch_pagan": float(bp_stat),
        "breusch_pagan_p": float(bp_pvalue),
    }
