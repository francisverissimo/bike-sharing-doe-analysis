"""Plot factorial effects, the key interaction, ANOVA, and weather post-hoc tests."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from statsmodels.stats.multicomp import pairwise_tukeyhsd

from bike_sharing.config import FIGURES_DIR, TABLES_DIR, ensure_output_directories
from bike_sharing.data import load_hourly_data
from bike_sharing.models import fit_model
from bike_sharing.plotting import configure_style, save_figure
from bike_sharing.statistics import add_partial_eta_squared, grouped_summary


def save_weather_tukey(data: pd.DataFrame) -> pd.DataFrame:
    """Compare the three pooled weather conditions on the log response."""
    result = pairwise_tukeyhsd(data["log1p_cnt"], data["weather_group"])
    summary = result.summary()
    table = pd.DataFrame(summary.data[1:], columns=summary.data[0])
    table.to_csv(TABLES_DIR / "tukey_log1p_by_weather_group.csv", index=False)
    return table


def plot_main_effects(data: pd.DataFrame) -> None:
    figure, axes = plt.subplots(2, 2, figsize=(11, 7))
    specifications = [
        ("hr", "Hour"),
        ("workingday_label", "Working-day status"),
        ("weather_group", "Weather condition"),
        ("season_label", "Season"),
    ]
    for axis, (factor, label) in zip(axes.flat, specifications):
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
        axis.set(title=label, xlabel=label, ylabel="Mean hourly rentals")
    figure.tight_layout()
    save_figure(figure, FIGURES_DIR / "main_effects.png")


def plot_workingday_hour_interaction(data: pd.DataFrame) -> None:
    figure, axis = plt.subplots(figsize=(9, 4.8))
    sns.lineplot(
        data=data,
        x="hr",
        y="cnt",
        hue="workingday_label",
        estimator="mean",
        errorbar=("ci", 95),
        seed=42,
        ax=axis,
    )
    axis.set(
        title="Working-day status by hour interaction",
        ylabel="Mean hourly rentals",
        xlabel="Hour",
    )
    axis.legend(frameon=False, title=None, ncol=2)
    axis.set_xticks(range(0, 24, 2))
    figure.tight_layout()
    save_figure(figure, FIGURES_DIR / "workingday_hr_interaction.png")


def main() -> None:
    ensure_output_directories()
    configure_style()
    data = load_hourly_data()

    model = fit_model(data, target="log1p_cnt")
    anova = add_partial_eta_squared(sm.stats.anova_lm(model, typ=2))
    anova.to_csv(TABLES_DIR / "factorial_anova.csv")

    tukey = save_weather_tukey(data)

    plot_main_effects(data)
    plot_workingday_hour_interaction(data)
    print(f"Main effects, interaction, ANOVA, and {len(tukey)} Tukey contrasts written.")


if __name__ == "__main__":
    main()
