"""Create readable result summaries from the generated analysis tables."""

from __future__ import annotations

import pandas as pd

from bike_sharing.config import OUTPUT_DIR, TABLES_DIR, ensure_output_directories


def format_p_value(value: float) -> str:
    """Format p-values without reporting numerical zero."""
    return "$<0.001$" if value < 0.001 else f"{value:.3f}"


def format_pt_br(value: float, decimals: int = 2) -> str:
    """Format a number with Brazilian decimal and thousands separators."""
    formatted = f"{value:,.{decimals}f}"
    return formatted.replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")


ANOVA_LABELS = {
    "C(hr)": "Hour",
    "C(workingday)": "Working day",
    "C(weather_group)": "Weather condition",
    "C(season)": "Season",
    "C(hr):C(workingday)": "Hour x working day",
    "temp": "Temperature",
    "hum": "Humidity",
    "windspeed": "Wind speed",
}
def build_anova_table() -> pd.DataFrame:
    """Prepare the final-model factorial ANOVA table."""
    anova = pd.read_csv(TABLES_DIR / "factorial_anova.csv").rename(
        columns={"Unnamed: 0": "term", "partial_eta_sq": "eta"}
    )
    anova = anova[anova["term"].isin(ANOVA_LABELS)][["term", "df", "F", "PR(>F)", "eta"]].rename(
        columns={"PR(>F)": "p-value", "eta": "Partial eta-squared"}
    )
    anova["term"] = anova["term"].map(ANOVA_LABELS)
    anova["df"] = anova["df"].astype(int)
    anova["p-value"] = anova["p-value"].map(format_p_value)
    return anova.rename(columns={"term": "Term"})


def main() -> None:
    ensure_output_directories()

    response = pd.read_csv(TABLES_DIR / "response_summary.csv").set_index("statistic")["value"]
    weather = pd.read_csv(TABLES_DIR / "summary_by_weather.csv").set_index("weather_group")["mean"]
    anova = build_anova_table()
    tukey = pd.read_csv(TABLES_DIR / "tukey_log1p_by_weather_group.csv")
    test = pd.read_csv(TABLES_DIR / "test_metrics.csv").iloc[0]
    model = pd.read_csv(TABLES_DIR / "model_summary.csv").iloc[0]
    checks = pd.read_csv(TABLES_DIR / "diagnostic_tests.csv").iloc[0]
    eta = anova.set_index("Term")["Partial eta-squared"]
    tukey_rejections = int(tukey["reject"].sum())
    selected = str(model["selected_model"])

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

## Design, ANOVA and model sequence

- One-way ANOVAs are reported for the four factors on `log1p(cnt)`.
- Hour has partial eta-squared {eta['Hour']:.3f}; hour by working day has
  {eta['Hour x working day']:.3f}.
- Weather condition and season have partial eta-squared
  {eta['Weather condition']:.3f} and {eta['Season']:.3f}, respectively.
- Tukey HSD on `log1p(cnt)` compares the three pooled weather conditions;
  all {tukey_rejections} of {len(tukey)} adjusted contrasts are significant.
- M0--M3 were compared on the 2011 training data. BIC selected {selected}, which
  is retained as M4; the selected model uses {int(model['parameters'])} parameters,
  adjusted R-squared {model['adjusted_r_squared']:.3f},
  AIC {model['aic']:.1f}, and BIC {model['bic']:.1f}.
- Residual ACF is {checks['acf_lag_1']:.3f} at lag 1, {checks['acf_lag_24']:.3f} at lag
  24, and {checks['acf_lag_168']:.3f} at lag 168.
- Durbin--Watson is {checks['durbin_watson']:.3f}; maximum VIF is
  {checks['vif_max']:.1f}; Levene and Bartlett tests are significant.

## Response scale and prediction

- Four scales were compared: raw, square root, `log1p(cnt)` and Box--Cox
  (estimated exponent {checks['boxcox_lambda']:.3f}).
- `log1p(cnt)` was retained for its best test accuracy and direct interpretation.
- Training uses {int(test['train_n']):,} hours in 2011; the test set contains
  {int(test['test_n']):,} hours in 2012.
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

## Delineamento, ANOVA e sequência de modelos

- ANOVA one-way é reportada para os quatro fatores em `log1p(cnt)`.
- A hora possui eta quadrado parcial {format_pt_br(eta['Hour'], 3)} e a interação
  hora por tipo de dia, {format_pt_br(eta['Hour x working day'], 3)}.
- Condição climática e estação apresentam eta quadrado parcial
  {format_pt_br(eta['Weather condition'], 3)} e
  {format_pt_br(eta['Season'], 3)}, respectivamente.
- O teste de Tukey HSD em `log1p(cnt)` compara as três condições climáticas
  agrupadas; todas as {tukey_rejections} de {len(tukey)} comparações ajustadas
  são significativas.
- M0--M3 foram comparados nos dados de treino de 2011. O BIC selecionou
  {selected}, mantido como M4; o modelo selecionado usa
  {format_pt_br(model['parameters'], 0)} parâmetros, com $R^2$ ajustado
  {format_pt_br(model['adjusted_r_squared'], 3)}, AIC
  {format_pt_br(model['aic'], 1)} e BIC {format_pt_br(model['bic'], 1)}.
- A ACF residual é {format_pt_br(checks['acf_lag_1'], 3)} na defasagem 1,
  {format_pt_br(checks['acf_lag_24'], 3)} na defasagem 24 e
  {format_pt_br(checks['acf_lag_168'], 3)} na defasagem 168.
- Durbin--Watson é {format_pt_br(checks['durbin_watson'], 3)}; o VIF máximo é
  {format_pt_br(checks['vif_max'], 1)}; Levene e Bartlett são significativos.

## Escala da resposta e predição

- Quatro escalas foram comparadas: bruta, raiz quadrada, `log1p(cnt)` e
  Box--Cox (expoente estimado {format_pt_br(checks['boxcox_lambda'], 3)}).
- `log1p(cnt)` foi mantida pela melhor acurácia no teste e interpretação direta.
- O treino usa {format_pt_br(test['train_n'], 0)} horas em 2011; o teste contém
  {format_pt_br(test['test_n'], 0)} horas em 2012.
- MAE {format_pt_br(test['mae'])}, RMSE {format_pt_br(test['rmse'])} e
  $R^2$ {format_pt_br(test['r2'], 3)} no teste.

Os resultados representam associações e previsões em dados observacionais não
randomizados; eles não demonstram causalidade.
"""
    (OUTPUT_DIR / "resumo_resultados.md").write_text(summary_pt, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
