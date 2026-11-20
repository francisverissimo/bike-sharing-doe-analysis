# Presentation outline

## 1. Research problem

- Explain why hourly bike demand matters.
- State the explanatory and predictive objectives.

## 2. Dataset

- Capital Bikeshare, Washington, D.C., 2011--2012.
- 17,379 observed hours and 731 calendar days.
- Response: total hourly rentals (`cnt`).

## 3. Study design

- Observational, unrandomized, naturally factorial, temporally dependent.
- Unit of observation: one recorded hour.
- Associations and predictions, not causal effects.

## 4. Factors and hypotheses

- `hr`, `workingday`, `weathersit`, `season`, plus `temp`, `hum`, `windspeed`, `yr`.
- Primary hypothesis: `workingday × hr`.
- Explain why OFAT would miss the commuting pattern.

## 5. Descriptive results

- Mean 189.46, median 142, range 1--977, skewness 1.277.
- Show weather and seasonal means.

## 6. Main effects and interaction

- Show `main_effects.png` and `workingday_hr_interaction.png`.
- Interpret morning/evening working-day peaks and the non-working-day midday peak.
- Report partial eta-squared 0.589 for the interaction.

## 7. Response scale and factorial ANOVA

- Compare `cnt` with `log1p(cnt)`: adjusted R-squared 0.812 versus 0.927.
- Breusch--Pagan 4281.6 versus 1676.6.
- Report hour 0.878, weather 0.120, season 0.168, year 0.264.

## 8. Regression and residual diagnostics

- Show the single model formula with 58 parameters.
- Residual ACF: 0.612 at lag 1, 0.243 at lag 24, 0.200 at lag 168.
- Emphasise that the test set carries the predictive evidence.

## 9. Temporal prediction

- Train through 30 September 2012; test on Q4 2012 (2,168 hours).
- Show `test_predictions.png`.
- MAE 45.27, RMSE 72.97, test R-squared 0.869.

## 10. Conclusions and limitations

- Working-day by hour is the central structural interaction.
- Weather, season, temperature, and year add adjustment.
- No randomization; residual dependence remains; severe weather is sparse.
- List final refinements before submission.
