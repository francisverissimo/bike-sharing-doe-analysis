# Results summary

## Data and descriptive analysis

- 17,379 observed hours from 2011 to 2012.
- Mean `cnt`: 189.46; median: 142;
  standard deviation: 181.39.
- Range: 1--977 rentals per hour;
  skewness 1.277.
- 165 timestamps are absent from the hourly calendar; no imputation was applied.
- Weather levels 3 and 4 are pooled because level 4 has only three observations.
- Mean rentals by weather condition: clear/partly cloudy
  204.87, mist/cloudy 175.17,
  precipitation/adverse 111.50.

## Design, ANOVA and model sequence

- One-way ANOVAs are reported for the four factors on `log1p(cnt)`.
- Hour has partial eta-squared 0.866; hour by working day has
  0.569.
- Weather condition and season have partial eta-squared
  0.124 and 0.197, respectively.
- Tukey HSD on `log1p(cnt)` compares the three pooled weather conditions;
  all 3 of 3 adjusted contrasts are significant.
- M0--M3 were compared on the 2011 training data. BIC selected M1, which
  is retained as M4; the selected model uses 56 parameters,
  adjusted R-squared 0.920,
  AIC 8277.9, and BIC 8673.5.
- Residual ACF is 0.593 at lag 1, 0.201 at lag
  24, and 0.138 at lag 168.
- Durbin--Watson is 0.814; maximum VIF is
  24.0; Levene and Bartlett tests are significant.

## Response scale and prediction

- Four scales were compared: raw, square root, `log1p(cnt)` and Box--Cox
  (estimated exponent 0.315).
- `log1p(cnt)` was retained for its best test accuracy and direct interpretation.
- Training uses 8,645 hours in 2011; the test set contains
  8,734 hours in 2012.
- Test MAE 87.67, RMSE 125.19, and
  R-squared 0.641.

These are associations and predictions from non-randomized observational data;
they do not establish causal effects.
