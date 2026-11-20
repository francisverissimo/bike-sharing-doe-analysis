"""Generate descriptive statistics and plots for the hourly rental count."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from bike_sharing.config import FIGURES_DIR, TABLES_DIR, ensure_output_directories
from bike_sharing.data import load_hourly_data
from bike_sharing.plotting import configure_style, save_figure
from bike_sharing.statistics import grouped_summary

FACTORS = {
    "hr": "hr",
    "workingday": "workingday_label",
    "weathersit": "weather_label",
    "season": "season_label",
}


def save_tables(data: pd.DataFrame) -> None:
    response = data["cnt"]
    summary = pd.DataFrame(
        {
            "statistic": [
                "n",
                "mean",
                "median",
                "std",
                "min",
                "q1",
                "q3",
                "max",
                "skewness",
                "excess_kurtosis",
            ],
            "value": [
                response.count(),
                response.mean(),
                response.median(),
                response.std(),
                response.min(),
                response.quantile(0.25),
                response.quantile(0.75),
                response.max(),
                response.skew(),
                response.kurtosis(),
            ],
        }
    )
    summary.to_csv(TABLES_DIR / "response_summary.csv", index=False)

    for filename, group in FACTORS.items():
        grouped_summary(data, group).to_csv(
            TABLES_DIR / f"summary_by_{filename}.csv", index=False
        )

    data[["cnt", "temp", "atemp", "hum", "windspeed"]].corr().to_csv(
        TABLES_DIR / "numeric_correlations.csv"
    )


def plot_response_distribution(data: pd.DataFrame) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    sns.histplot(data=data, x="cnt", bins=50, kde=True, ax=axes[0], color="#2563eb")
    axes[0].set(title="Hourly rental count", xlabel="Total rentals (cnt)", ylabel="Hours")
    sns.histplot(data=data, x="log1p_cnt", bins=50, kde=True, ax=axes[1], color="#059669")
    axes[1].set(title="Log-transformed rental count", xlabel="log(1 + cnt)", ylabel="Hours")
    figure.tight_layout()
    save_figure(figure, FIGURES_DIR / "response_distributions.png")


def plot_factor_boxplots(data: pd.DataFrame) -> None:
    figure, axes = plt.subplots(2, 2, figsize=(11, 7.5))
    specifications = [
        ("hr", "Hour of day", "#c4b5fd"),
        ("workingday_label", "Working-day status", "#93c5fd"),
        ("weather_label", "Weather situation", "#a7f3d0"),
        ("season_label", "Season", "#fde68a"),
    ]
    for axis, (column, title, color) in zip(axes.flat, specifications):
        sns.boxplot(data=data, x=column, y="cnt", ax=axis, color=color, fliersize=1)
        axis.set(xlabel="", ylabel="Hourly rentals", title=title)
        if column != "hr":
            axis.tick_params(axis="x", rotation=15)
    figure.tight_layout()
    save_figure(figure, FIGURES_DIR / "factor_boxplots.png")


def plot_time_series(data: pd.DataFrame) -> None:
    daily = data.groupby("dteday", as_index=False).agg(mean_hourly_cnt=("cnt", "mean"))
    rolling = daily["mean_hourly_cnt"].rolling(14, center=True, min_periods=1).mean()
    figure, axis = plt.subplots(figsize=(11, 3.8))
    axis.plot(daily["dteday"], daily["mean_hourly_cnt"], color="#94a3b8", alpha=0.45)
    axis.plot(daily["dteday"], rolling, color="#1d4ed8", linewidth=1.7, label="14-day mean")
    axis.axvline(pd.Timestamp("2012-01-01"), color="#dc2626", linestyle="--", linewidth=1)
    axis.set(
        title="Daily evolution of mean hourly demand",
        xlabel="Date",
        ylabel="Mean hourly rentals",
    )
    axis.legend(frameon=False)
    figure.tight_layout()
    save_figure(figure, FIGURES_DIR / "daily_time_series.png")


def plot_correlations(data: pd.DataFrame) -> None:
    columns = ["cnt", "temp", "atemp", "hum", "windspeed"]
    figure, axis = plt.subplots(figsize=(6.5, 5))
    sns.heatmap(
        data[columns].corr(),
        annot=True,
        fmt=".2f",
        cmap="vlag",
        center=0,
        vmin=-1,
        vmax=1,
        square=True,
        ax=axis,
    )
    axis.set_title("Pearson correlations")
    figure.tight_layout()
    save_figure(figure, FIGURES_DIR / "numeric_correlations.png")


def main() -> None:
    ensure_output_directories()
    configure_style()
    data = load_hourly_data()
    save_tables(data)
    plot_response_distribution(data)
    plot_factor_boxplots(data)
    plot_time_series(data)
    plot_correlations(data)
    print("Descriptive outputs written to outputs/figures and outputs/tables.")


if __name__ == "__main__":
    main()
