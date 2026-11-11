"""Compare candidate response scales and diagnose linear-model assumptions."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tsa.stattools import acf

from bike_sharing.config import DIAGNOSTICS_DIR, TABLES_DIR, ensure_output_directories
from bike_sharing.data import load_hourly_data
from bike_sharing.models import EXPLANATORY_FORMULAS
from bike_sharing.plotting import configure_style, save_figure
from bike_sharing.statistics import residual_diagnostics


def transformation_models(data: pd.DataFrame) -> dict[str, object]:
    formula = EXPLANATORY_FORMULAS["M1_workingday_hour"]
    return {
        target: smf.ols(formula.format(target=target), data=data).fit()
        for target in ("cnt", "sqrt_cnt", "log1p_cnt")
    }


def save_vif_tables(data: pd.DataFrame) -> None:
    for label, columns in {
        "candidate": ["temp", "atemp", "hum", "windspeed"],
        "selected": ["temp", "hum", "windspeed"],
    }.items():
        design = sm.add_constant(data[columns])
        table = pd.DataFrame(
            {
                "variable": design.columns,
                "vif": [
                    variance_inflation_factor(design.to_numpy(), index)
                    for index in range(design.shape[1])
                ],
            }
        )
        table.to_csv(TABLES_DIR / f"vif_{label}_numeric_predictors.csv", index=False)


def plot_model_diagnostics(models: dict[str, object]) -> None:
    figure, axes = plt.subplots(3, 3, figsize=(12, 11))
    for row, (target, model) in enumerate(models.items()):
        fitted = np.asarray(model.fittedvalues)
        residuals = np.asarray(model.resid)
        sns.scatterplot(x=fitted, y=residuals, s=5, alpha=0.18, ax=axes[row, 0])
        axes[row, 0].axhline(0, color="black", linewidth=0.8)
        axes[row, 0].set(title=f"{target}: residuals vs fitted", xlabel="Fitted", ylabel="Residual")
        sm.qqplot(residuals, line="45", fit=True, ax=axes[row, 1])
        axes[row, 1].set_title(f"{target}: normal Q-Q")
        scale = np.sqrt(np.abs(residuals / np.std(residuals, ddof=1)))
        sns.scatterplot(x=fitted, y=scale, s=5, alpha=0.18, ax=axes[row, 2])
        axes[row, 2].set(
            title=f"{target}: scale-location", xlabel="Fitted", ylabel="sqrt(|std resid|)"
        )
    figure.tight_layout()
    save_figure(figure, DIAGNOSTICS_DIR / "transformation_diagnostics.png")


def plot_temporal_diagnostics(model: object) -> None:
    residuals = np.asarray(model.resid)
    correlations = acf(residuals, nlags=168, fft=True)
    table = pd.DataFrame({"lag": np.arange(len(correlations)), "acf": correlations})
    table.to_csv(TABLES_DIR / "residual_acf_log_model.csv", index=False)

    figure, axis = plt.subplots(figsize=(10, 4))
    axis.stem(table["lag"], table["acf"], markerfmt=" ", basefmt=" ")
    bound = 1.96 / np.sqrt(len(residuals))
    axis.axhline(bound, color="#dc2626", linestyle="--", linewidth=0.8)
    axis.axhline(-bound, color="#dc2626", linestyle="--", linewidth=0.8)
    axis.set(
        title="Residual autocorrelation for the log-response model",
        xlabel="Lag (observed hours)",
        ylabel="ACF",
        xlim=(0, 168),
    )
    figure.tight_layout()
    save_figure(figure, DIAGNOSTICS_DIR / "residual_acf_log_model.png")


def main() -> None:
    ensure_output_directories()
    configure_style()
    data = load_hourly_data()
    models = transformation_models(data)

    diagnostics = pd.DataFrame(
        residual_diagnostics(model, target) for target, model in models.items()
    )
    diagnostics["r_squared_adj"] = [model.rsquared_adj for model in models.values()]
    diagnostics.to_csv(TABLES_DIR / "transformation_diagnostics.csv", index=False)

    boxcox_lambda = stats.boxcox_normmax(data["cnt"], method="mle")
    pd.DataFrame({"method": ["Box-Cox MLE"], "lambda": [boxcox_lambda]}).to_csv(
        TABLES_DIR / "boxcox_lambda.csv", index=False
    )
    save_vif_tables(data)
    plot_model_diagnostics(models)
    plot_temporal_diagnostics(models["log1p_cnt"])
    print(diagnostics.to_string(index=False))


if __name__ == "__main__":
    main()
