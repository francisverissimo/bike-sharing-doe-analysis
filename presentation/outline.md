# MVP presentation outline

## 1. Research problem

- Explain why hourly bike demand matters.
- State the explanatory and predictive objectives.

## 2. Dataset

- Capital Bikeshare, Washington, D.C., 2011–2012.
- 17,379 observed hours and 731 calendar days.
- Response: total hourly rentals (`cnt`).

## 3. Study design

- Observational, unrandomized, naturally factorial, temporally dependent.
- Unit of observation: one recorded hour.
- Associations and predictions, not causal effects.

## 4. Factors and hypotheses

- Hour, working-day status, weather, season, temperature, humidity, wind.
- Primary hypothesis: `hour × working day`.
- Explain why OFAT would miss the commuting pattern.

## 5. Descriptive results

- Show `response_distributions.png`.
- Report mean 189.46, median 142, range 1–977.
- Show weather and seasonal means.

## 6. Main effects and interactions

- Show `interaction_plots.png`.
- Interpret morning/evening working-day peaks and the non-working-day midday peak.
- Report partial eta-squared 0.615 for the primary interaction.

## 7. Assumptions and model construction

- Compare raw, square-root, and log-one-plus scales.
- Explain remaining heteroscedasticity and autocorrelation.
- Mention HAC(168) uncertainty and the no-causality limitation.

## 8. Explanatory model

- Show the M0–M4 comparison.
- M4 adjusted R-squared 0.935 on the log response.
- Explain why high in-sample fit does not guarantee the best predictor.

## 9. Temporal prediction

- Explain Q2/Q3 expanding-window selection and untouched Q4 holdout.
- Show `holdout_predictions.png`.
- P1: MAE 50.18, RMSE 81.65, out-of-sample R-squared 0.836.

## 10. Conclusions and limitations

- Hour by working day is the central structural interaction.
- Weather and temperature contribute additional information.
- No randomization; residual dependence remains; extreme weather is sparse.
- List final refinements before submission.
