"""Statistical summaries, ANOVA helpers, and full residual diagnostics."""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson
from statsmodels.tsa.stattools import acf, pacf


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


def one_way_anova(
    data: pd.DataFrame, factors: list[str], response: str = "log1p_cnt"
) -> pd.DataFrame:
    """Fit one-way ANOVAs and report eta-squared and omega-squared per factor."""
    rows: list[dict[str, float | int | str]] = []
    for factor in factors:
        model = smf.ols(f"{response} ~ C({factor})", data=data).fit()
        table = sm.stats.anova_lm(model, typ=1)
        term = f"C({factor})"
        between_ss = float(table.loc[term, "sum_sq"])
        between_df = int(table.loc[term, "df"])
        residual_ss = float(table.loc["Residual", "sum_sq"])
        residual_df = float(table.loc["Residual", "df"])
        residual_ms = residual_ss / residual_df
        eta_sq = between_ss / (between_ss + residual_ss)
        omega_sq = (between_ss - between_df * residual_ms) / (
            between_ss + residual_ss + residual_ms
        )
        rows.append(
            {
                "factor": factor,
                "df": between_df,
                "F": float(table.loc[term, "F"]),
                "p_value": float(table.loc[term, "PR(>F)"]),
                "eta_sq": float(eta_sq),
                "omega_sq": float(omega_sq),
            }
        )
    return pd.DataFrame(rows)


def residual_diagnostics(model: object, label: str) -> dict[str, float | str]:
    """Calculate residual normality and constant-variance diagnostics."""
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


def homoscedasticity_group_tests(model: object, *, groups: int = 5) -> dict[str, float]:
    """Test residual variance equality across fitted-value quintiles."""
    residuals = np.asarray(model.resid)
    bins = pd.qcut(np.asarray(model.fittedvalues), groups, labels=False, duplicates="drop")
    samples = [residuals[np.asarray(bins == level)] for level in np.unique(bins)]
    levene_stat, levene_p = stats.levene(*samples, center="median")
    bartlett_stat, bartlett_p = stats.bartlett(*samples)
    return {
        "levene_stat": float(levene_stat),
        "levene_p": float(levene_p),
        "bartlett_stat": float(bartlett_stat),
        "bartlett_p": float(bartlett_p),
        "variance_groups": len(samples),
    }


def correlation_table(model: object, nlags: int = 168) -> pd.DataFrame:
    """Return ACF and PACF values at observed-hour lags."""
    residuals = np.asarray(model.resid)
    return pd.DataFrame(
        {
            "lag": np.arange(nlags + 1),
            "acf": acf(residuals, nlags=nlags, fft=True),
            "pacf": pacf(residuals, nlags=nlags, method="ywm"),
        }
    )


def durbin_watson_statistic(model: object) -> float:
    """Return the Durbin--Watson statistic for model residuals."""
    return float(durbin_watson(np.asarray(model.resid)))


def variance_inflation_table(model: object) -> pd.DataFrame:
    """Calculate VIF for every non-intercept design-matrix column."""
    design = np.asarray(model.model.exog)
    rows: list[dict[str, float | str]] = []
    for index, name in enumerate(model.model.exog_names):
        if name == "Intercept":
            continue
        rows.append({"term": str(name), "vif": float(variance_inflation_factor(design, index))})
    return pd.DataFrame(rows).sort_values("vif", ascending=False).reset_index(drop=True)


def influence_summary(model: object) -> dict[str, float | int]:
    """Summarise leverage and Cook's distance with standard screening thresholds."""
    influence = model.get_influence()
    leverage = np.asarray(influence.hat_matrix_diag)
    cooks = np.asarray(influence.cooks_distance[0])
    n = int(model.nobs)
    parameters = int(len(model.params))
    return {
        "max_leverage": float(np.max(leverage)),
        "leverage_above_2p_n": int(np.sum(leverage > 2 * parameters / n)),
        "max_cooks_d": float(np.max(cooks)),
        "cooks_above_4_n": int(np.sum(cooks > 4 / n)),
        "leverage_threshold": float(2 * parameters / n),
        "cooks_threshold": float(4 / n),
    }
