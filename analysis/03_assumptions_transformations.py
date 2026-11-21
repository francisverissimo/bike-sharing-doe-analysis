"""Compare response transformations and run the full diagnostic checklist."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from statsmodels.graphics.gofplots import qqplot

from bike_sharing.config import (
    CANDIDATE_SCALES,
    DIAGNOSTICS_DIR,
    TABLES_DIR,
    TRAIN_END,
    ensure_output_directories,
)
from bike_sharing.data import load_hourly_data
from bike_sharing.models import (
    compare_models,
    fit_model,
    fit_model_sequence,
    select_model_by_bic,
)
from bike_sharing.plotting import configure_style, save_figure
from bike_sharing.statistics import (
    correlation_table,
    durbin_watson_statistic,
    homoscedasticity_group_tests,
    influence_summary,
    residual_diagnostics,
    variance_inflation_table,
)
from bike_sharing.transforms import add_candidate_responses

SCALE_LABELS = {
    "cnt": "$cnt$",
    "sqrt_cnt": "$\\sqrt{cnt}$",
    "log1p_cnt": "$\\log(1+cnt)$",
    "boxcox_cnt": "Box--Cox",
}


def plot_scale_diagnostics(models: dict[str, object]) -> None:
    """Show residual-versus-fitted and Q--Q panels for all candidate scales."""
    figure, axes = plt.subplots(2, 4, figsize=(16, 7))
    for column, scale in enumerate(CANDIDATE_SCALES):
        model = models[scale]
        fitted = np.asarray(model.fittedvalues)
        residuals = np.asarray(model.resid)

        fitted_axis = axes[0, column]
        sns.scatterplot(x=fitted, y=residuals, s=4, alpha=0.16, ax=fitted_axis)
        fitted_axis.axhline(0, color="black", linewidth=0.8)
        fitted_axis.set(
            title=f"{SCALE_LABELS[scale]}: residuals",
            xlabel="Fitted",
            ylabel="Residual",
        )

        qq_axis = axes[1, column]
        qqplot(residuals, line="45", fit=True, ax=qq_axis)
        qq_axis.set_title(f"{SCALE_LABELS[scale]}: Q--Q")
    figure.tight_layout()
    save_figure(figure, DIAGNOSTICS_DIR / "scale_residual_diagnostics.png")
    plt.close(figure)


def plot_correlations(correlations: pd.DataFrame, n: int) -> None:
    """Plot residual ACF and PACF on observed-hour lags."""
    for column, title, filename in (
        ("acf", "Residual autocorrelation", "residual_acf.png"),
        ("pacf", "Residual partial autocorrelation", "residual_pacf.png"),
    ):
        figure, axis = plt.subplots(figsize=(10, 4))
        axis.stem(correlations["lag"], correlations[column], markerfmt=" ", basefmt=" ")
        bound = 1.96 / np.sqrt(n)
        axis.axhline(bound, color="#dc2626", linestyle="--", linewidth=0.8)
        axis.axhline(-bound, color="#dc2626", linestyle="--", linewidth=0.8)
        axis.set(
            title=title,
            xlabel="Lag (observed hours)",
            ylabel=column.upper(),
            xlim=(0, 168),
        )
        figure.tight_layout()
        save_figure(figure, DIAGNOSTICS_DIR / filename)
        plt.close(figure)


def plot_influence(
    influence: dict[str, float | int], leverage: np.ndarray, cooks: np.ndarray
) -> None:
    """Plot leverage against Cook's distance with screening thresholds."""
    figure, axis = plt.subplots(figsize=(7, 5))
    axis.scatter(leverage, cooks, s=6, alpha=0.25)
    axis.axhline(influence["cooks_threshold"], color="#dc2626", linestyle="--", linewidth=0.8)
    axis.axvline(influence["leverage_threshold"], color="#dc2626", linestyle="--", linewidth=0.8)
    axis.set(
        title="Influence diagnostics",
        xlabel="Leverage",
        ylabel="Cook's distance",
    )
    figure.tight_layout()
    save_figure(figure, DIAGNOSTICS_DIR / "influence_diagnostics.png")
    plt.close(figure)


def main() -> None:
    ensure_output_directories()
    configure_style()
    data = load_hourly_data()
    train = data.loc[data["timestamp"] <= pd.Timestamp(TRAIN_END)].copy()
    train, lam = add_candidate_responses(train)

    sequence = fit_model_sequence(train, target="log1p_cnt")
    comparison = compare_models(sequence)
    selected = select_model_by_bic(sequence)
    comparison["selected"] = comparison["model"] == selected
    comparison.to_csv(TABLES_DIR / "model_sequence.csv", index=False)
    final_model = sequence[selected]

    scale_models = {
        scale: fit_model(train, target=scale, model=selected) for scale in CANDIDATE_SCALES
    }
    diagnostics = pd.DataFrame(
        residual_diagnostics(model, scale) for scale, model in scale_models.items()
    )
    diagnostics["adjusted_r_squared"] = [
        float(model.rsquared_adj) for model in scale_models.values()
    ]
    diagnostics["aic"] = [float(model.aic) for model in scale_models.values()]
    diagnostics["bic"] = [float(model.bic) for model in scale_models.values()]
    diagnostics["boxcox_lambda"] = lam
    diagnostics.to_csv(TABLES_DIR / "scale_comparison.csv", index=False)
    plot_scale_diagnostics(scale_models)

    correlations = correlation_table(final_model, nlags=168)
    correlations.to_csv(TABLES_DIR / "residual_acf.csv", index=False)
    correlations[["lag", "pacf"]].to_csv(TABLES_DIR / "residual_pacf.csv", index=False)
    plot_correlations(correlations, len(train))

    variance = homoscedasticity_group_tests(final_model)
    influence = influence_summary(final_model)
    vif = variance_inflation_table(final_model)
    vif.to_csv(TABLES_DIR / "vif.csv", index=False)

    influence_values = final_model.get_influence()
    leverage = np.asarray(influence_values.hat_matrix_diag)
    cooks = np.asarray(influence_values.cooks_distance[0])
    plot_influence(influence, leverage, cooks)

    basic = residual_diagnostics(final_model, "log1p_cnt")
    by_lag = correlations.set_index("lag")
    checks = {
        **basic,
        **variance,
        **influence,
        "durbin_watson": durbin_watson_statistic(final_model),
        "acf_lag_1": float(by_lag.loc[1, "acf"]),
        "acf_lag_24": float(by_lag.loc[24, "acf"]),
        "acf_lag_168": float(by_lag.loc[168, "acf"]),
        "pacf_lag_1": float(by_lag.loc[1, "pacf"]),
        "pacf_lag_24": float(by_lag.loc[24, "pacf"]),
        "pacf_lag_168": float(by_lag.loc[168, "pacf"]),
        "vif_max": float(vif["vif"].max()),
        "vif_median": float(vif["vif"].median()),
        "boxcox_lambda": lam,
    }
    pd.DataFrame([checks]).to_csv(TABLES_DIR / "diagnostic_tests.csv", index=False)

    print(comparison.to_string(index=False))
    print(diagnostics.to_string(index=False))
    print(pd.Series(checks).to_string())


if __name__ == "__main__":
    main()
