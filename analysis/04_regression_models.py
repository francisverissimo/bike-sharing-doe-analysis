"""Fit, compare, and diagnose the hierarchical explanatory regression models."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.anova import anova_lm

from bike_sharing.config import DIAGNOSTICS_DIR, TABLES_DIR, ensure_output_directories
from bike_sharing.data import load_hourly_data
from bike_sharing.models import fit_explanatory_models
from bike_sharing.plotting import configure_style, save_figure
from bike_sharing.statistics import (
    add_partial_eta_squared,
    nested_model_table,
    residual_diagnostics,
)


def model_summary_table(models: dict[str, object]) -> pd.DataFrame:
    rows = []
    for name, model in models.items():
        rows.append(
            {
                "model": name,
                "parameters": int(model.df_model + 1),
                "r_squared": model.rsquared,
                "adjusted_r_squared": model.rsquared_adj,
                "aic": model.aic,
                "bic": model.bic,
                "residual_std": np.sqrt(model.mse_resid),
            }
        )
    return pd.DataFrame(rows)


def save_robust_coefficients(model: object) -> None:
    robust = model.get_robustcov_results(cov_type="HAC", maxlags=168)
    confidence = robust.conf_int()
    table = pd.DataFrame(
        {
            "term": model.model.exog_names,
            "coefficient": robust.params,
            "standard_error_hac168": robust.bse,
            "ci95_low": confidence[:, 0],
            "ci95_high": confidence[:, 1],
            "p_value_hac168": robust.pvalues,
        }
    )
    table.to_csv(TABLES_DIR / "final_explanatory_hac168_coefficients.csv", index=False)


def plot_final_diagnostics(model: object) -> None:
    fitted = np.asarray(model.fittedvalues)
    residuals = np.asarray(model.resid)
    influence = model.get_influence()
    cooks_distance = influence.cooks_distance[0]
    leverage = influence.hat_matrix_diag

    pd.DataFrame(
        {
            "observation": np.arange(len(residuals)),
            "studentized_residual": influence.resid_studentized_internal,
            "leverage": leverage,
            "cooks_distance": cooks_distance,
        }
    ).nlargest(25, "cooks_distance").to_csv(
        TABLES_DIR / "top_influential_observations.csv", index=False
    )

    figure, axes = plt.subplots(2, 2, figsize=(11, 8))
    axes[0, 0].hexbin(fitted, residuals, gridsize=55, mincnt=1, cmap="Blues")
    axes[0, 0].axhline(0, color="black", linewidth=0.8)
    axes[0, 0].set(title="Residuals vs fitted", xlabel="Fitted log count", ylabel="Residual")
    sm.qqplot(residuals, line="45", fit=True, ax=axes[0, 1])
    axes[0, 1].set_title("Normal Q-Q")
    axes[1, 0].scatter(leverage, influence.resid_studentized_internal, s=5, alpha=0.2)
    axes[1, 0].set(title="Residuals vs leverage", xlabel="Leverage", ylabel="Studentized residual")
    axes[1, 1].scatter(np.arange(len(cooks_distance)), cooks_distance, s=4, alpha=0.35)
    axes[1, 1].axhline(4 / len(cooks_distance), color="#dc2626", linestyle="--")
    axes[1, 1].set(title="Cook's distance", xlabel="Observation", ylabel="Cook's D")
    figure.tight_layout()
    save_figure(figure, DIAGNOSTICS_DIR / "final_explanatory_diagnostics.png")


def main() -> None:
    ensure_output_directories()
    configure_style()
    data = load_hourly_data()
    models = fit_explanatory_models(data, target="log1p_cnt")

    model_summary_table(models).to_csv(TABLES_DIR / "explanatory_model_comparison.csv", index=False)
    nested_model_table(models).to_csv(TABLES_DIR / "nested_model_tests.csv", index=False)

    final_name = "M1_workingday_hour"
    final_model = models[final_name]
    add_partial_eta_squared(anova_lm(final_model, typ=2)).to_csv(
        TABLES_DIR / "final_explanatory_anova.csv"
    )
    pd.DataFrame([residual_diagnostics(final_model, final_name)]).to_csv(
        TABLES_DIR / "final_explanatory_diagnostics.csv", index=False
    )
    save_robust_coefficients(final_model)
    plot_final_diagnostics(final_model)
    summary_lines = [
        line.rstrip()
        for line in final_model.summary().as_text().splitlines()
        if not line.lstrip().startswith(("Date:", "Time:"))
    ]
    (TABLES_DIR / "final_explanatory_model.txt").write_text(
        "\n".join(summary_lines) + "\n", encoding="utf-8"
    )
    print(model_summary_table(models).to_string(index=False))


if __name__ == "__main__":
    main()
