"""Evaluate the single model on one strictly chronological train/test split."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from bike_sharing.config import FIGURES_DIR, TABLES_DIR, ensure_output_directories
from bike_sharing.data import load_hourly_data
from bike_sharing.models import fit_model, predict_count_with_smearing, prediction_metrics
from bike_sharing.plotting import configure_style, save_figure

TRAIN_END = "2012-09-30 23:59:59"
TEST_START = "2012-10-01"
TEST_END = "2012-12-31 23:59:59"


def plot_predictions(test: pd.DataFrame) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    sns.scatterplot(
        data=test,
        x="cnt",
        y="predicted",
        hue="workingday_label",
        s=12,
        alpha=0.35,
        ax=axes[0],
    )
    limit = max(test["cnt"].max(), test["predicted"].max())
    axes[0].plot([0, limit], [0, limit], color="black", linestyle="--", linewidth=1)
    axes[0].set(
        title="Test set: observed vs predicted",
        xlabel="Observed hourly rentals",
        ylabel="Predicted hourly rentals",
    )
    axes[0].legend(frameon=False, title=None)

    daily = test.groupby("dteday", as_index=False).agg(
        observed=("cnt", "mean"), predicted=("predicted", "mean")
    )
    axes[1].plot(daily["dteday"], daily["observed"], label="Observed", color="#1d4ed8")
    axes[1].plot(daily["dteday"], daily["predicted"], label="Predicted", color="#dc2626")
    axes[1].set(
        title="Test set: daily mean hourly demand",
        xlabel="Date",
        ylabel="Mean hourly rentals",
    )
    axes[1].tick_params(axis="x", rotation=25)
    axes[1].legend(frameon=False)
    figure.tight_layout()
    save_figure(figure, FIGURES_DIR / "test_predictions.png")


def main() -> None:
    ensure_output_directories()
    configure_style()
    data = load_hourly_data()
    train = data.loc[data["timestamp"] <= pd.Timestamp(TRAIN_END)].copy()
    test = data.loc[
        data["timestamp"].between(pd.Timestamp(TEST_START), pd.Timestamp(TEST_END))
    ].copy()

    model = fit_model(train, target="log1p_cnt")
    predicted = predict_count_with_smearing(model, test)
    metrics = prediction_metrics(test["cnt"], predicted)

    result = pd.DataFrame(
        [
            {
                "train_n": len(train),
                "test_n": len(test),
                "train_end": TRAIN_END,
                "test_start": TEST_START,
                "test_end": TEST_END,
                **metrics,
            }
        ]
    )
    result.to_csv(TABLES_DIR / "test_metrics.csv", index=False)

    test["predicted"] = predicted
    test["residual"] = test["cnt"] - test["predicted"]
    test[
        ["timestamp", "cnt", "predicted", "residual", "hr", "workingday", "weathersit"]
    ].to_csv(TABLES_DIR / "test_predictions.csv", index=False)

    plot_predictions(test)
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
