"""Create LaTeX tables and readable result summaries for both article versions."""

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


ANOVA_LABELS = {
    "C(hr)": "Hour",
    "C(workingday)": "Working day",
    "C(weather_group)": "Weather condition",
    "C(season)": "Season",
    "C(yr)": "Year",
    "C(hr):C(workingday)": "Hour x working day",
    "temp": "Temperature",
    "hum": "Humidity",
    "windspeed": "Wind speed",
}


def main() -> None:
    ensure_output_directories()

    response = pd.read_csv(TABLES_DIR / "response_summary.csv").set_index("statistic")["value"]
    weather = pd.read_csv(TABLES_DIR / "summary_by_weather.csv").set_index("weather_group")["mean"]
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

    anova = pd.read_csv(TABLES_DIR / "factorial_anova.csv").rename(
        columns={"Unnamed: 0": "term", "partial_eta_sq": "eta"}
    )
    anova = anova[anova["term"].isin(ANOVA_LABELS)][
        ["term", "df", "F", "PR(>F)", "eta"]
    ].rename(columns={"PR(>F)": "p-value", "eta": "Partial eta-squared"})
    anova["term"] = anova["term"].map(ANOVA_LABELS)
    anova["df"] = anova["df"].astype(int)
    anova["p-value"] = anova["p-value"].map(format_p_value)
    anova = anova.rename(columns={"term": "Term"})
    write_latex(anova, "paper_anova.tex", "lrrlr", escape=False)

    tukey = pd.read_csv(TABLES_DIR / "tukey_log1p_by_weather_group.csv")
    # statsmodels reports group2 minus group1; flip so the table reads group1 minus group2.
    tukey_table = pd.DataFrame(
        {
            "Comparison": [
                f"{first} vs {second}"
                for first, second in zip(tukey["group1"], tukey["group2"])
            ],
            "Difference": -tukey["meandiff"],
            "95% CI": [
                f"[{-high:.3f}, {-low:.3f}]"
                for low, high in zip(tukey["lower"], tukey["upper"])
            ],
            "Adjusted $p$": tukey["p-adj"].map(format_p_value),
        }
    )
    write_latex(tukey_table, "paper_tukey.tex", "lrrlr", escape=False)

    scales = pd.read_csv(TABLES_DIR / "scale_comparison.csv").set_index("scale")
    scale_table = pd.DataFrame(
        {
            "Response": [r"$cnt$", r"$\log(1+cnt)$"],
            "Adjusted $R^2$": [
                f"{scales.loc['cnt', 'adjusted_r_squared']:.3f}",
                f"{scales.loc['log1p_cnt', 'adjusted_r_squared']:.3f}",
            ],
            "Shapiro--Wilk $W$ ($p$)": [
                format_test_stat(
                    scales.loc[scale, "shapiro_w_5000"], scales.loc[scale, "shapiro_p_5000"], 3
                )
                for scale in ("cnt", "log1p_cnt")
            ],
            "Breusch--Pagan LM ($p$)": [
                format_test_stat(
                    scales.loc[scale, "breusch_pagan"], scales.loc[scale, "breusch_pagan_p"], 1
                )
                for scale in ("cnt", "log1p_cnt")
            ],
        }
    )
    write_latex(scale_table, "paper_scale_comparison.tex", "lrrr", escape=False)

    test = pd.read_csv(TABLES_DIR / "test_metrics.csv").iloc[0]
    test_table = pd.DataFrame(
        {
            "MAE": [test["mae"]],
            "RMSE": [test["rmse"]],
            "Test $R^2$": [test["r2"]],
        }
    )
    write_latex(test_table, "paper_test_metrics.tex", "rrr", escape=False)

    model = pd.read_csv(TABLES_DIR / "model_summary.csv").iloc[0]
    acf = pd.read_csv(TABLES_DIR / "residual_acf.csv").set_index("lag")["acf"]
    eta = anova.set_index("Term")["Partial eta-squared"]
    tukey_rejections = int(tukey["reject"].sum())

    summary = f"""# Results summary

## Data and descriptive analysis

- {int(response['n']):,} observed hours from 2011 to 2012.
- Mean `cnt`: {response['mean']:.2f}; median: {response['median']:.0f};
  standard deviation: {response['std']:.2f}.
- Range: {response['min']:.0f}--{response['max']:.0f} rentals per hour;
  skewness {response['skewness']:.3f}.
- 165 timestamps are absent from the hourly calendar; no imputation was applied.
- Weather levels 3 and 4 are pooled because level 4 has only three observations.
- Mean rentals by weather condition: clear/partly cloudy
  {weather['Clear/partly cloudy']:.2f}, mist/cloudy {weather['Mist/cloudy']:.2f},
  precipitation/adverse {weather['Precipitation/adverse']:.2f}.

## Factorial analysis

- Hour has partial eta-squared {eta['Hour']:.3f}; hour by working day has
  {eta['Hour x working day']:.3f}.
- Weather condition and season have partial eta-squared
  {eta['Weather condition']:.3f} and {eta['Season']:.3f}, respectively.
- Tukey HSD on `log1p(cnt)` compares the three pooled weather conditions;
  all {tukey_rejections} of {len(tukey)} adjusted contrasts are significant.
- The single log-response model uses {int(model['parameters'])} parameters,
  adjusted R-squared {model['adjusted_r_squared']:.3f},
  AIC {model['aic']:.1f}, and BIC {model['bic']:.1f}.
- Residual ACF is {acf[1]:.3f} at lag 1, {acf[24]:.3f} at lag 24, and
  {acf[168]:.3f} at lag 168.

## Response scale and prediction

- Adjusted R-squared is {scales.loc['cnt', 'adjusted_r_squared']:.3f} for `cnt` and
  {scales.loc['log1p_cnt', 'adjusted_r_squared']:.3f} for `log1p(cnt)`.
- Training uses {int(test['train_n']):,} hours through September 2012; the test
  set contains {int(test['test_n']):,} hours in the final quarter of 2012.
- Test MAE {test['mae']:.2f}, RMSE {test['rmse']:.2f}, and
  R-squared {test['r2']:.3f}.

These are associations and predictions from non-randomized observational data;
they do not establish causal effects.
"""
    (OUTPUT_DIR / "results_summary.md").write_text(summary, encoding="utf-8")

    summary_pt = f"""# Resumo dos resultados

## Dados e análise descritiva

- {format_pt_br(response['n'], 0)} horas observadas entre 2011 e 2012.
- Média de `cnt`: {format_pt_br(response['mean'])}; mediana:
  {format_pt_br(response['median'], 0)}; desvio-padrão: {format_pt_br(response['std'])}.
- Intervalo: {format_pt_br(response['min'], 0)}--{format_pt_br(response['max'], 0)}
  aluguéis por hora; assimetria {format_pt_br(response['skewness'], 3)}.
- Há 165 horários ausentes no calendário; não foi feita imputação.
- Os níveis 3 e 4 foram agrupados porque o nível 4 tem apenas três observações.
- Média de aluguéis por condição climática: claro/parcialmente nublado
  {format_pt_br(weather['Clear/partly cloudy'])}, névoa/nublado
  {format_pt_br(weather['Mist/cloudy'])} e precipitação/tempo adverso
  {format_pt_br(weather['Precipitation/adverse'])}.

## Análise fatorial

- A hora possui eta quadrado parcial {format_pt_br(eta['Hour'], 3)} e a interação
  hora por tipo de dia, {format_pt_br(eta['Hour x working day'], 3)}.
- Condição climática e estação apresentam eta quadrado parcial
  {format_pt_br(eta['Weather condition'], 3)} e
  {format_pt_br(eta['Season'], 3)}, respectivamente.
- O teste de Tukey HSD em `log1p(cnt)` compara as três condições climáticas
  agrupadas; todas as {tukey_rejections} de {len(tukey)} comparações ajustadas
  são significativas.
- O único modelo na escala logarítmica usa
  {format_pt_br(model['parameters'], 0)} parâmetros, com $R^2$ ajustado
  {format_pt_br(model['adjusted_r_squared'], 3)}, AIC
  {format_pt_br(model['aic'], 1)} e BIC {format_pt_br(model['bic'], 1)}.
- A ACF residual é {format_pt_br(acf[1], 3)} na defasagem 1,
  {format_pt_br(acf[24], 3)} na defasagem 24 e {format_pt_br(acf[168], 3)} na
  defasagem 168.

## Escala da resposta e predição

- O $R^2$ ajustado é {format_pt_br(scales.loc['cnt', 'adjusted_r_squared'], 3)} para
  `cnt` e {format_pt_br(scales.loc['log1p_cnt', 'adjusted_r_squared'], 3)} para
  `log1p(cnt)`.
- O treino usa {format_pt_br(test['train_n'], 0)} horas até setembro de 2012; o
  teste contém {format_pt_br(test['test_n'], 0)} horas no último trimestre de 2012.
- MAE {format_pt_br(test['mae'])}, RMSE {format_pt_br(test['rmse'])} e
  $R^2$ {format_pt_br(test['r2'], 3)} no teste.

Os resultados representam associações e previsões em dados observacionais não
randomizados; eles não demonstram causalidade.
"""
    (OUTPUT_DIR / "resumo_resultados.md").write_text(summary_pt, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
