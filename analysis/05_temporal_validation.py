"""Select and evaluate predictive regressions using chronology-preserving splits."""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from bike_sharing.config import FIGURES_DIR, TABLES_DIR, ensure_output_directories
from bike_sharing.data import load_hourly_data
from bike_sharing.models import (
    PREDICTIVE_FORMULAS,
    fit_predictive_model,
    predict_count_with_smearing,
    prediction_metrics,
)
from bike_sharing.plotting import configure_style, save_figure

SPLITS = [
    ("validation_q2_2012", "2012-03-31 23:59:59", "2012-04-01", "2012-06-30 23:59:59"),
    ("validation_q3_2012", "2012-06-30 23:59:59", "2012-07-01", "2012-09-30 23:59:59"),
    ("holdout_q4_2012", "2012-09-30 23:59:59", "2012-10-01", "2012-12-31 23:59:59"),
]


def baseline_predictions(training: pd.DataFrame, evaluation: pd.DataFrame) -> np.ndarray:
    """Predict historical means for each hour and working-day combination."""
    lookup = training.groupby(["hr", "workingday"], observed=True)["cnt"].mean()
    fallback = float(training["cnt"].mean())
    return np.array(
        [
            lookup.get((hour, workingday), fallback)
            for hour, workingday in zip(evaluation["hr"], evaluation["workingday"])
        ]
    )


def evaluate_split(
    data: pd.DataFrame,
    split_name: str,
    training_end: str,
    evaluation_start: str,
    evaluation_end: str,
) -> tuple[list[dict[str, float | int | str]], dict[str, np.ndarray]]:
    training = data.loc[data["timestamp"] <= pd.Timestamp(training_end)].copy()
    evaluation = data.loc[
        data["timestamp"].between(pd.Timestamp(evaluation_start), pd.Timestamp(evaluation_end))
    ].copy()

    rows: list[dict[str, float | int | str]] = []
    predictions: dict[str, np.ndarray] = {}
    baseline = baseline_predictions(training, evaluation)
    predictions["baseline_hour_workingday"] = baseline
    rows.append(
        {
            "split": split_name,
            "model": "baseline_hour_workingday",
            "training_n": len(training),
            "evaluation_n": len(evaluation),
            **prediction_metrics(evaluation["cnt"], baseline),
        }
    )

    for model_name, formula in PREDICTIVE_FORMULAS.items():
        model = fit_predictive_model(formula, training)
        predicted = predict_count_with_smearing(model, evaluation)
        predictions[model_name] = predicted
        rows.append(
            {
                "split": split_name,
                "model": model_name,
                "training_n": len(training),
                "evaluation_n": len(evaluation),
                **prediction_metrics(evaluation["cnt"], predicted),
            }
        )
    return rows, predictions


def subgroup_errors(
    evaluation: pd.DataFrame, predicted: np.ndarray, model_name: str
) -> pd.DataFrame:
    frame = evaluation[["hr", "workingday", "weather_group", "cnt"]].copy()
    frame["predicted"] = predicted
    frame["absolute_error"] = np.abs(frame["cnt"] - frame["predicted"])
    outputs = []
    for factor in ("hr", "workingday", "weather_group"):
        grouped = frame.groupby(factor, observed=True).agg(
            n=("cnt", "size"),
            mae=("absolute_error", "mean"),
            observed_mean=("cnt", "mean"),
            predicted_mean=("predicted", "mean"),
        )
        grouped = grouped.reset_index().rename(columns={factor: "level"})
        grouped.insert(0, "factor", factor)
        outputs.append(grouped)
    result = pd.concat(outputs, ignore_index=True)
    result.insert(0, "model", model_name)
    return result


def plot_holdout_predictions(evaluation: pd.DataFrame) -> None:
    """Visualize pointwise and daily holdout predictions."""
    figure, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    sns.scatterplot(
        data=evaluation,
        x="cnt",
        y="predicted",
        hue="workingday_label",
        s=12,
        alpha=0.35,
        ax=axes[0],
    )
    limit = max(evaluation["cnt"].max(), evaluation["predicted"].max())
    axes[0].plot([0, limit], [0, limit], color="black", linestyle="--", linewidth=1)
    axes[0].set(
        title="Q4 2012: observed vs predicted",
        xlabel="Observed hourly rentals",
        ylabel="Predicted hourly rentals",
    )
    axes[0].legend(frameon=False, title=None)

    daily = evaluation.groupby("dteday", as_index=False).agg(
        observed=("cnt", "mean"), predicted=("predicted", "mean")
    )
    axes[1].plot(daily["dteday"], daily["observed"], label="Observed", color="#1d4ed8")
    axes[1].plot(daily["dteday"], daily["predicted"], label="Predicted", color="#dc2626")
    axes[1].set(
        title="Q4 2012: daily mean hourly demand",
        xlabel="Date",
        ylabel="Mean hourly rentals",
    )
    axes[1].tick_params(axis="x", rotation=25)
    axes[1].legend(frameon=False)
    figure.tight_layout()
    save_figure(figure, FIGURES_DIR / "holdout_predictions.png")


def main() -> None:
    ensure_output_directories()
    configure_style()
    data = load_hourly_data()
    all_rows: list[dict[str, float | int | str]] = []
    prediction_store: dict[str, tuple[pd.DataFrame, dict[str, np.ndarray]]] = {}

    for split in SPLITS:
        rows, predictions = evaluate_split(data, *split)
        all_rows.extend(rows)
        start, end = pd.Timestamp(split[2]), pd.Timestamp(split[3])
        evaluation = data.loc[data["timestamp"].between(start, end)].copy()
        prediction_store[split[0]] = (evaluation, predictions)

    results = pd.DataFrame(all_rows)
    results.to_csv(TABLES_DIR / "temporal_validation_results.csv", index=False)

    validation = results[results["split"].str.startswith("validation")]
    ranking = (
        validation.groupby("model", as_index=False)
        .agg(mean_mae=("mae", "mean"), mean_rmse=("rmse", "mean"), mean_r2=("r2", "mean"))
        .sort_values(["mean_rmse", "mean_mae"])
    )
    ranking.to_csv(TABLES_DIR / "predictive_model_ranking.csv", index=False)
    selected = str(ranking.iloc[0]["model"])

    holdout = results[(results["split"] == "holdout_q4_2012") & (results["model"] == selected)]
    holdout.to_csv(TABLES_DIR / "final_holdout_result.csv", index=False)
    evaluation, predictions = prediction_store["holdout_q4_2012"]
    evaluation["predicted"] = predictions[selected]
    evaluation["residual"] = evaluation["cnt"] - evaluation["predicted"]
    evaluation[
        [
            "timestamp",
            "cnt",
            "predicted",
            "residual",
            "hr",
            "workingday",
            "weather_group",
        ]
    ].to_csv(TABLES_DIR / "final_holdout_predictions.csv", index=False)
    subgroup_errors(evaluation, predictions[selected], selected).to_csv(
        TABLES_DIR / "final_holdout_subgroup_errors.csv", index=False
    )
    plot_holdout_predictions(evaluation)

    selection = {
        "selection_rule": "lowest mean RMSE across Q2 and Q3 2012 expanding-window validation",
        "selected_model": selected,
        "holdout_period": "2012-10-01 through 2012-12-31",
        "holdout_evaluated_after_selection": True,
    }
    (TABLES_DIR / "predictive_model_selection.json").write_text(
        json.dumps(selection, indent=2) + "\n", encoding="utf-8"
    )
    print(ranking.to_string(index=False))
    print("\nSelected model:", selected)
    print(holdout.to_string(index=False))


if __name__ == "__main__":
    main()
