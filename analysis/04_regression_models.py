"""Fit the single prespecified log-response regression model."""

from __future__ import annotations

import numpy as np
import pandas as pd

from bike_sharing.config import TABLES_DIR, ensure_output_directories
from bike_sharing.data import load_hourly_data
from bike_sharing.models import fit_model

TARGET = "log1p_cnt"


def main() -> None:
    ensure_output_directories()
    data = load_hourly_data()
    model = fit_model(data, target=TARGET)

    summary = pd.DataFrame(
        {
            "target": [TARGET],
            "parameters": [int(model.df_model + 1)],
            "r_squared": [model.rsquared],
            "adjusted_r_squared": [model.rsquared_adj],
            "aic": [model.aic],
            "bic": [model.bic],
            "residual_std": [float(np.sqrt(model.mse_resid))],
        }
    )
    summary.to_csv(TABLES_DIR / "model_summary.csv", index=False)

    summary_lines = [
        line.rstrip()
        for line in model.summary().as_text().splitlines()
        if not line.lstrip().startswith(("Date:", "Time:"))
    ]
    (TABLES_DIR / "model_summary.txt").write_text(
        "\n".join(summary_lines) + "\n", encoding="utf-8"
    )
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
