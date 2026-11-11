# MVP results summary

## Data

- 17,379 hourly observations from 2011–2012.
- Mean `cnt`: 189.46; median: 142; SD: 181.39.
- Range: 1–977 rentals per observed hour.
- 165 timestamps are absent from the otherwise hourly calendar sequence.
- Weather levels 3 and 4 are combined for inference; level 4 has only three rows.

## Descriptive effects

- Clear/partly cloudy mean: 204.87 rentals/hour.
- Mist/cloudy mean: 175.17 rentals/hour.
- Precipitation/adverse mean: 111.50 rentals/hour.
- `temp` and `atemp` correlate at 0.988, supporting exclusion of `atemp`.

## DOE and explanatory regression

- The primary `hour × working day` interaction has partial eta-squared 0.615.
- Hour has partial eta-squared 0.890 in the full hierarchical model.
- The full MVP model has adjusted R-squared 0.935,
  AIC 14188.4, and BIC 15531.4 on `log1p(cnt)`.
- Residual Durbin–Watson is 0.861; temporal
  dependence remains and HAC(168) uncertainty is therefore reported.

## Prediction

- P1 (`hour × working day`, without the extra weather-by-hour interaction) won
  selection on Q2/Q3 2012 expanding-window validation.
- On the untouched Q4 2012 holdout (n=2168), P1 achieved
  MAE 50.18, RMSE 81.65, R-squared 0.836,
  and RMSLE 0.501.

These findings are associations from non-randomized observational data and do
not establish causal effects.
