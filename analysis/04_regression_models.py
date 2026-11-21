"""Fit the BIC-selected model from the M0--M4 sequence on the training year."""

from __future__ import annotations

import numpy as np
import pandas as pd

from bike_sharing.config import FINAL_RESPONSE, TABLES_DIR, TRAIN_END, ensure_output_directories
from bike_sharing.data import load_hourly_data
from bike_sharing.models import fit_model


def main() -> None:
    ensure_output_directories()
    data = load_hourly_data()
    train = data.loc[data["timestamp"] <= pd.Timestamp(TRAIN_END)].copy()
    sequence = pd.read_csv(TABLES_DIR / "model_sequence.csv")
    selected = str(sequence.loc[sequence["selected"], "model"].iloc[0])

    model = fit_model(train, target=FINAL_RESPONSE, model=selected)
    summary = pd.DataFrame(
        {
            "selected_model": [selected],
            "target": [FINAL_RESPONSE],
            "parameters": [int(model.df_model + 1)],
            "r_squared": [float(model.rsquared)],
            "adjusted_r_squared": [float(model.rsquared_adj)],
            "aic": [float(model.aic)],
            "bic": [float(model.bic)],
            "residual_std": [float(np.sqrt(model.mse_resid))],
        }
    )
    summary.to_csv(TABLES_DIR / "model_summary.csv", index=False)

    summary_lines = [
        line.rstrip()
        for line in model.summary().as_text().splitlines()
        if not line.lstrip().startswith(("Date:", "Time:"))
    ]
    (TABLES_DIR / "model_summary.txt").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
