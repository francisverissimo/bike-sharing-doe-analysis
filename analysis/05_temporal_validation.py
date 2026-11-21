"""Validate the selected model on a strictly chronological 2011/2012 split."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from bike_sharing.config import (
    CANDIDATE_SCALES,
    FIGURES_DIR,
    FINAL_RESPONSE,
    TABLES_DIR,
    TEST_END,
    TEST_START,
    TRAIN_END,
    ensure_output_directories,
)
from bike_sharing.data import load_hourly_data
from bike_sharing.models import fit_model, predict_count, prediction_metrics
from bike_sharing.plotting import configure_style, save_figure
from bike_sharing.transforms import add_candidate_responses


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
        title="2012 test set: observed vs predicted",
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
        title="2012 test set: daily mean hourly demand",
        xlabel="Date",
        ylabel="Mean hourly rentals",
    )
    axes[1].tick_params(axis="x", rotation=25)
    axes[1].legend(frameon=False)
    figure.tight_layout()
    save_figure(figure, FIGURES_DIR / "test_predictions.png")
    plt.close(figure)


def main() -> None:
    ensure_output_directories()
    configure_style()
    data = load_hourly_data()
    train = data.loc[data["timestamp"] <= pd.Timestamp(TRAIN_END)].copy()
    test = data.loc[
        data["timestamp"].between(pd.Timestamp(TEST_START), pd.Timestamp(TEST_END))
    ].copy()
    train, lam = add_candidate_responses(train)
    test, _ = add_candidate_responses(test, lam=lam)

    sequence = pd.read_csv(TABLES_DIR / "model_sequence.csv")
    selected = str(sequence.loc[sequence["selected"], "model"].iloc[0])

    scale_rows: list[dict[str, float | str | int]] = []
    final_predictions = None
    for scale in CANDIDATE_SCALES:
        model = fit_model(train, target=scale, model=selected)
        predicted = predict_count(model, test, target=scale, lam=lam)
        scale_rows.append(
            {
                "scale": scale,
                "parameters": int(model.df_model + 1),
                **prediction_metrics(test["cnt"], predicted),
            }
        )
        if scale == FINAL_RESPONSE:
            final_predictions = predicted

    scale_metrics = pd.DataFrame(scale_rows)
    scale_metrics.to_csv(TABLES_DIR / "scale_test_metrics.csv", index=False)

    train_n, test_n = len(train), len(test)
    observed = test["cnt"].to_numpy(dtype=float)
    metrics = prediction_metrics(observed, final_predictions)
    test_metrics = pd.DataFrame(
        [
            {
                "selected_model": selected,
                "response": FINAL_RESPONSE,
                "train_n": train_n,
                "test_n": test_n,
                "train_end": TRAIN_END,
                "test_start": TEST_START,
                "test_end": TEST_END,
                **metrics,
            }
        ]
    )
    test_metrics.to_csv(TABLES_DIR / "test_metrics.csv", index=False)

    test["predicted"] = final_predictions
    test["residual"] = test["cnt"] - test["predicted"]
    test[["timestamp", "cnt", "predicted", "residual", "hr", "workingday", "weathersit"]].to_csv(
        TABLES_DIR / "test_predictions.csv", index=False
    )

    plot_predictions(test)
    print(test_metrics.to_string(index=False))
    print(scale_metrics.to_string(index=False))


if __name__ == "__main__":
    main()
