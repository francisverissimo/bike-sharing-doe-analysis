"""Estimate main effects and interactions using a DOE-informed observational analysis."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.multicomp import pairwise_tukeyhsd

from bike_sharing.config import FIGURES_DIR, TABLES_DIR, ensure_output_directories
from bike_sharing.data import load_hourly_data
from bike_sharing.models import EXPLANATORY_FORMULAS
from bike_sharing.plotting import configure_style, save_figure
from bike_sharing.statistics import add_partial_eta_squared, grouped_summary


def one_way_tests(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for factor in ("workingday", "weather_group", "season"):
        for response in ("cnt", "log1p_cnt"):
            samples = [
                group[response].to_numpy()
                for _, group in data.groupby(factor, observed=True)
            ]
            f_statistic, anova_p = stats.f_oneway(*samples)
            levene_statistic, levene_p = stats.levene(*samples, center="median")
            rows.append(
                {
                    "factor": factor,
                    "response": response,
                    "f_statistic": f_statistic,
                    "anova_p": anova_p,
                    "levene_statistic": levene_statistic,
                    "levene_p": levene_p,
                }
            )
    return pd.DataFrame(rows)


def save_tukey(data: pd.DataFrame, factor: str) -> None:
    result = pairwise_tukeyhsd(data["log1p_cnt"], data[factor])
    table = pd.DataFrame(result.summary().data[1:], columns=result.summary().data[0])
    table.to_csv(TABLES_DIR / f"tukey_log1p_by_{factor}.csv", index=False)


def plot_main_effects(data: pd.DataFrame) -> None:
    figure, axes = plt.subplots(2, 2, figsize=(11, 7))
    specifications = [
        ("hr", "Hour", "Hour of day"),
        ("workingday_label", "Working-day status", "Working day"),
        ("weather_group", "Weather", "Weather conditions"),
        ("season_label", "Season", "Season"),
    ]
    for axis, (factor, xlabel, title) in zip(axes.flat, specifications):
        summary = grouped_summary(data, factor)
        x = range(len(summary))
        axis.errorbar(
            x,
            summary["mean"],
            yerr=[
                summary["mean"] - summary["ci95_low"],
                summary["ci95_high"] - summary["mean"],
            ],
            marker="o",
            capsize=2,
            linewidth=1.5,
            color="#1d4ed8",
        )
        axis.set_xticks(list(x), summary[factor])
        if factor != "hr":
            axis.tick_params(axis="x", rotation=15)
        axis.set(title=title, xlabel=xlabel, ylabel="Mean hourly rentals")
    figure.tight_layout()
    save_figure(figure, FIGURES_DIR / "main_effects.png")


def plot_interactions(data: pd.DataFrame) -> None:
    figure, axes = plt.subplots(3, 1, figsize=(10, 11), sharex=True)
    sns.lineplot(
        data=data,
        x="hr",
        y="cnt",
        hue="workingday_label",
        estimator="mean",
        errorbar=("ci", 95),
        seed=42,
        ax=axes[0],
    )
    axes[0].set(title="Hour × working-day status", ylabel="Mean hourly rentals", xlabel="")
    sns.lineplot(
        data=data,
        x="hr",
        y="cnt",
        hue="weather_group",
        estimator="mean",
        errorbar=None,
        ax=axes[1],
    )
    axes[1].set(title="Hour × weather", ylabel="Mean hourly rentals", xlabel="")
    sns.lineplot(
        data=data,
        x="hr",
        y="cnt",
        hue="season_label",
        estimator="mean",
        errorbar=None,
        ax=axes[2],
    )
    axes[2].set(title="Hour × season", ylabel="Mean hourly rentals", xlabel="Hour")
    for axis in axes:
        axis.legend(frameon=False, title=None, ncol=2)
        axis.set_xticks(range(0, 24, 2))
    figure.tight_layout()
    save_figure(figure, FIGURES_DIR / "interaction_plots.png")


def main() -> None:
    ensure_output_directories()
    configure_style()
    data = load_hourly_data()

    one_way_tests(data).to_csv(TABLES_DIR / "one_way_tests.csv", index=False)
    save_tukey(data, "season")
    save_tukey(data, "weather_group")

    formula_m1 = EXPLANATORY_FORMULAS["M1_workingday_hour"].format(target="log1p_cnt")
    factorial_model = smf.ols(formula_m1, data=data).fit()
    factorial_anova = add_partial_eta_squared(anova_lm(factorial_model, typ=2))
    factorial_anova.to_csv(TABLES_DIR / "factorial_anova_primary.csv")

    robust = factorial_model.get_robustcov_results(cov_type="HAC", maxlags=24)
    robust_table = pd.DataFrame(
        {
            "term": factorial_model.model.exog_names,
            "coefficient": robust.params,
            "standard_error_hac24": robust.bse,
            "p_value_hac24": robust.pvalues,
        }
    )
    robust_table.to_csv(TABLES_DIR / "primary_model_hac24_coefficients.csv", index=False)

    plot_main_effects(data)
    plot_interactions(data)
    print("DOE outputs generated: main effects, interactions, ANOVA, Tukey, and HAC inference.")


if __name__ == "__main__":
    main()
