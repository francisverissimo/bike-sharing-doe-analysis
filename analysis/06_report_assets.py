"""Create concise LaTeX tables and a readable MVP results summary."""

from __future__ import annotations

import pandas as pd

from bike_sharing.config import OUTPUT_DIR, TABLES_DIR, ensure_output_directories


def write_latex(
    frame: pd.DataFrame, filename: str, column_format: str, *, escape: bool = True
) -> None:
    latex = frame.to_latex(
        index=False,
        escape=escape,
        float_format=lambda value: f"{value:.3f}",
        column_format=column_format,
    )
    (TABLES_DIR / filename).write_text(latex, encoding="utf-8")


def format_p_value(value: float) -> str:
    """Format p-values without reporting numerical zero."""
    return "$<0.001$" if value < 0.001 else f"{value:.3f}"


def main() -> None:
    ensure_output_directories()

    response = pd.read_csv(TABLES_DIR / "response_summary.csv").set_index("statistic")["value"]
    descriptive = pd.DataFrame(
        {
            "N": [int(response["n"])],
            "Mean": [response["mean"]],
            "Median": [response["median"]],
            "SD": [response["std"]],
            "Q1": [response["q1"]],
            "Q3": [response["q3"]],
            "Min": [response["min"]],
            "Max": [response["max"]],
        }
    )
    write_latex(descriptive, "paper_descriptive.tex", "rrrrrrrr")

    anova = pd.read_csv(TABLES_DIR / "final_explanatory_anova.csv").rename(
        columns={"Unnamed: 0": "Term", "partial_eta_sq": "Partial eta-squared"}
    )
    selected_terms = [
        "C(hr)",
        "C(workingday)",
        "C(weather_group)",
        "C(season)",
        "C(yr)",
        "C(hr):C(workingday)",
        "C(weather_group):C(hr)",
        "C(season):C(hr)",
        "temp",
        "I(temp ** 2)",
        "hum",
        "windspeed",
    ]
    anova = anova[anova["Term"].isin(selected_terms)][
        ["Term", "df", "F", "PR(>F)", "Partial eta-squared"]
    ].rename(columns={"PR(>F)": "p-value"})
    anova["Term"] = anova["Term"].replace(
        {
            "C(hr)": "Hour",
            "C(workingday)": "Working day",
            "C(weather_group)": "Weather",
            "C(season)": "Season",
            "C(yr)": "Year",
            "C(hr):C(workingday)": "Hour x working day",
            "C(weather_group):C(hr)": "Weather x hour",
            "C(season):C(hr)": "Season x hour",
            "temp": "Temperature",
            "I(temp ** 2)": "Temperature squared",
            "hum": "Humidity",
            "windspeed": "Wind speed",
        }
    )
    anova["p-value"] = anova["p-value"].map(format_p_value)
    write_latex(anova, "paper_anova.tex", "lrrlr", escape=False)

    models = pd.read_csv(TABLES_DIR / "explanatory_model_comparison.csv")[
        ["model", "parameters", "adjusted_r_squared", "aic", "bic"]
    ].rename(
        columns={
            "model": "Model",
            "parameters": "Parameters",
            "adjusted_r_squared": "Adjusted R-squared",
            "aic": "AIC",
            "bic": "BIC",
        }
    )
    models["Model"] = ["M0", "M1", "M2", "M3", "M4"]
    write_latex(models, "paper_models.tex", "lrrrr")

    validation = pd.read_csv(TABLES_DIR / "temporal_validation_results.csv")
    validation = validation[validation["split"] == "holdout_q4_2012"][
        ["model", "mae", "rmse", "r2", "rmsle"]
    ].rename(
        columns={
            "model": "Model",
            "mae": "MAE",
            "rmse": "RMSE",
            "r2": "R-squared",
            "rmsle": "RMSLE",
        }
    )
    validation["Model"] = ["Baseline", "P0", "P1", "P2"]
    write_latex(validation, "paper_holdout.tex", "lrrrr")

    final_diagnostics = pd.read_csv(TABLES_DIR / "final_explanatory_diagnostics.csv").iloc[0]
    final_model = models.iloc[-1]
    holdout = pd.read_csv(TABLES_DIR / "final_holdout_result.csv").iloc[0]
    weather = pd.read_csv(TABLES_DIR / "summary_by_weather.csv")
    summary = f"""# MVP results summary

## Data

- {int(response['n']):,} hourly observations from 2011–2012.
- Mean `cnt`: {response['mean']:.2f}; median: {response['median']:.0f}; SD: {response['std']:.2f}.
- Range: {response['min']:.0f}–{response['max']:.0f} rentals per observed hour.
- 165 timestamps are absent from the otherwise hourly calendar sequence.
- Weather levels 3 and 4 are combined for inference; level 4 has only three rows.

## Descriptive effects

- Clear/partly cloudy mean: {weather.iloc[0]['mean']:.2f} rentals/hour.
- Mist/cloudy mean: {weather.iloc[1]['mean']:.2f} rentals/hour.
- Precipitation/adverse mean: {weather.iloc[2]['mean']:.2f} rentals/hour.
- `temp` and `atemp` correlate at 0.988, supporting exclusion of `atemp`.

## DOE and explanatory regression

- The primary `hour × working day` interaction has partial eta-squared 0.615.
- Hour has partial eta-squared 0.890 in the full hierarchical model.
- The full MVP model has adjusted R-squared {final_model['Adjusted R-squared']:.3f},
  AIC {final_model['AIC']:.1f}, and BIC {final_model['BIC']:.1f} on `log1p(cnt)`.
- Residual Durbin–Watson is {final_diagnostics['durbin_watson']:.3f}; temporal
  dependence remains and HAC(168) uncertainty is therefore reported.

## Prediction

- P1 (`hour × working day`, without the extra weather-by-hour interaction) won
  selection on Q2/Q3 2012 expanding-window validation.
- On the untouched Q4 2012 holdout (n={int(holdout['evaluation_n'])}), P1 achieved
  MAE {holdout['mae']:.2f}, RMSE {holdout['rmse']:.2f}, R-squared {holdout['r2']:.3f},
  and RMSLE {holdout['rmsle']:.3f}.

These findings are associations from non-randomized observational data and do
not establish causal effects.
"""
    (OUTPUT_DIR / "mvp_results.md").write_text(summary, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
