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


def format_test_stat(stat: float, pvalue: float, decimals: int) -> str:
    """Combine a test statistic and its p-value in one LaTeX cell."""
    return f"{stat:.{decimals}f} ({format_p_value(pvalue)})"


def format_pt_br(value: float, decimals: int = 2) -> str:
    """Format a number with Brazilian decimal and thousands separators."""
    formatted = f"{value:,.{decimals}f}"
    return formatted.replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")


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

    diagnostics = pd.read_csv(TABLES_DIR / "transformation_diagnostics.csv")
    paper_diagnostics = pd.DataFrame(
        {
            "Scale": [r"cnt", r"$\sqrt{cnt}$", r"$\log(1+cnt)$"],
            "Shapiro--Wilk $W$ ($p$)": [
                format_test_stat(row.shapiro_w_5000, row.shapiro_p_5000, 3)
                for row in diagnostics.itertuples()
            ],
            "Breusch--Pagan LM ($p$)": [
                format_test_stat(row.breusch_pagan, row.breusch_pagan_p, 1)
                for row in diagnostics.itertuples()
            ],
            "Adjusted $R^2$": [f"{value:.3f}" for value in diagnostics["r_squared_adj"]],
        }
    )
    write_latex(paper_diagnostics, "paper_diagnostics.tex", "lrrr", escape=False)

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
        "temp",
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
            "temp": "Temperature",
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
    models["Model"] = ["M0", "M1"]
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
    validation["Model"] = ["Baseline", "P0", "P1"]
    write_latex(validation, "paper_holdout.tex", "lrrrr")

    final_model = models.iloc[-1]
    holdout = pd.read_csv(TABLES_DIR / "final_holdout_result.csv").iloc[0]
    weather = pd.read_csv(TABLES_DIR / "summary_by_weather.csv")
    acf = pd.read_csv(TABLES_DIR / "residual_acf_log_model.csv").set_index("lag")["acf"]
    interaction_eta = float(
        anova.loc[anova["Term"] == "Hour x working day", "Partial eta-squared"].iloc[0]
    )
    hour_eta = float(anova.loc[anova["Term"] == "Hour", "Partial eta-squared"].iloc[0])
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

- The primary `hour × working day` interaction has partial eta-squared {interaction_eta:.3f}.
- Hour has partial eta-squared {hour_eta:.3f} in M1.
- M1 has adjusted R-squared {final_model['Adjusted R-squared']:.3f},
  AIC {final_model['AIC']:.1f}, and BIC {final_model['BIC']:.1f} on `log1p(cnt)`.
- Residual ACF is {acf[1]:.3f} at lag 1, {acf[24]:.3f} at lag 24, and
  {acf[168]:.3f} at lag 168; HAC(168) uncertainty is therefore reported.

## Prediction

- P1 (`hour × working day`) won
  selection on Q2/Q3 2012 expanding-window validation.
- On the untouched Q4 2012 holdout (n={int(holdout['evaluation_n'])}), P1 achieved
  MAE {holdout['mae']:.2f}, RMSE {holdout['rmse']:.2f}, R-squared {holdout['r2']:.3f},
  and RMSLE {holdout['rmsle']:.3f}.

These findings are associations from non-randomized observational data and do
not establish causal effects.
"""
    (OUTPUT_DIR / "mvp_results.md").write_text(summary, encoding="utf-8")
    summary_pt = f"""# Resumo dos resultados do MVP simplificado

## Dados

- {format_pt_br(response['n'], 0)} observações horárias de 2011 a 2012.
- Média de `cnt`: {format_pt_br(response['mean'])}; mediana:
  {format_pt_br(response['median'], 0)}; desvio-padrão: {format_pt_br(response['std'])}.
- Intervalo: {format_pt_br(response['min'], 0)}–{format_pt_br(response['max'], 0)}
  aluguéis por hora observada.
- Há 165 timestamps ausentes na sequência horária; eles não foram imputados.
- Os níveis meteorológicos 3 e 4 foram agrupados; o nível 4 possui somente 3 casos.

## Resultados descritivos

- Média com tempo claro/parcialmente nublado: {format_pt_br(weather.iloc[0]['mean'])}.
- Média com névoa/nublado: {format_pt_br(weather.iloc[1]['mean'])}.
- Média com precipitação/tempo adverso: {format_pt_br(weather.iloc[2]['mean'])}.
- A correlação entre `temp` e `atemp` é 0,988; por isso `atemp` foi excluída.

## DOE e regressão explicativa

- A interação principal `hora × dia útil` possui eta quadrado parcial
  {format_pt_br(interaction_eta, 3)}.
- O fator hora possui eta quadrado parcial {format_pt_br(hour_eta, 3)} no M1.
- O M1 possui R² ajustado {format_pt_br(final_model['Adjusted R-squared'], 3)}, AIC
  {format_pt_br(final_model['AIC'], 1)} e BIC {format_pt_br(final_model['BIC'], 1)}
  para `log1p(cnt)`.
- A ACF residual é {format_pt_br(acf[1], 3)} na defasagem 1,
  {format_pt_br(acf[24], 3)} na defasagem 24 e {format_pt_br(acf[168], 3)} na
  defasagem 168; portanto são apresentados erros-padrão HAC(168).

## Predição

- O P1, que contém `hora × dia útil`, foi selecionado na validação expansiva de
  Q2 e Q3 de 2012.
- No holdout Q4/2012 (n={format_pt_br(holdout['evaluation_n'], 0)}), o P1 obteve
  MAE {format_pt_br(holdout['mae'])}, RMSE {format_pt_br(holdout['rmse'])}, R²
  {format_pt_br(holdout['r2'], 3)} e RMSLE {format_pt_br(holdout['rmsle'], 3)}.

Os resultados representam associações em dados observacionais não randomizados;
eles não demonstram causalidade.
"""
    (OUTPUT_DIR / "resultados_mvp-pt-br.md").write_text(summary_pt, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
