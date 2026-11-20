"""Compare cnt with log1p(cnt) and run basic residual diagnostics."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from statsmodels.tsa.stattools import acf

from bike_sharing.config import DIAGNOSTICS_DIR, TABLES_DIR, ensure_output_directories
from bike_sharing.data import load_hourly_data
from bike_sharing.models import fit_model
from bike_sharing.plotting import configure_style, save_figure
from bike_sharing.statistics import residual_diagnostics

SCALES = {"cnt": "cnt", "log1p_cnt": r"$\log(1+cnt)$"}


def plot_scale_diagnostics(models: dict[str, object]) -> None:
    figure, axes = plt.subplots(2, 2, figsize=(10, 8))
    for row, (target, model) in enumerate(models.items()):
        fitted = np.asarray(model.fittedvalues)
        residuals = np.asarray(model.resid)
        sns.scatterplot(x=fitted, y=residuals, s=5, alpha=0.18, ax=axes[row, 0])
        axes[row, 0].axhline(0, color="black", linewidth=0.8)
        axes[row, 0].set(
            title=f"{SCALES[target]}: residuals vs fitted",
            xlabel="Fitted",
            ylabel="Residual",
        )
        sm.qqplot(residuals, line="45", fit=True, ax=axes[row, 1])
        axes[row, 1].set_title(f"{SCALES[target]}: normal Q-Q")
    figure.tight_layout()
    save_figure(figure, DIAGNOSTICS_DIR / "scale_residual_diagnostics.png")


def plot_residual_acf(model: object) -> pd.DataFrame:
    residuals = np.asarray(model.resid)
    correlations = acf(residuals, nlags=168, fft=True)
    table = pd.DataFrame({"lag": np.arange(len(correlations)), "acf": correlations})
    table.to_csv(TABLES_DIR / "residual_acf.csv", index=False)

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
    save_figure(figure, DIAGNOSTICS_DIR / "residual_acf.png")
    return table


def main() -> None:
    ensure_output_directories()
    configure_style()
    data = load_hourly_data()
    models = {target: fit_model(data, target=target) for target in SCALES}

    diagnostics = pd.DataFrame(
        residual_diagnostics(model, target) for target, model in models.items()
    )
    diagnostics["adjusted_r_squared"] = [model.rsquared_adj for model in models.values()]
    diagnostics.to_csv(TABLES_DIR / "scale_comparison.csv", index=False)

    plot_scale_diagnostics(models)
    acf_table = plot_residual_acf(models["log1p_cnt"])
    print(diagnostics.to_string(index=False))
    print(acf_table.loc[acf_table["lag"].isin([1, 24, 168])].to_string(index=False))


if __name__ == "__main__":
    main()
