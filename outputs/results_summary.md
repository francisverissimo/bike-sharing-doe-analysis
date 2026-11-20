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

## Factorial analysis

- Hour has partial eta-squared 0.878; hour by working day has
  0.589.
- Weather condition and season have partial eta-squared
  0.120 and 0.168, respectively.
- Tukey HSD on `log1p(cnt)` compares the three pooled weather conditions;
  all 3 of 3 adjusted contrasts are significant.
- The single log-response model uses 57 parameters,
  adjusted R-squared 0.927,
  AIC 15914.2, and BIC 16356.7.
- Residual ACF is 0.612 at lag 1, 0.243 at lag 24, and
  0.200 at lag 168.

## Response scale and prediction

- Adjusted R-squared is 0.812 for `cnt` and
  0.927 for `log1p(cnt)`.
- Training uses 15,211 hours through September 2012; the test
  set contains 2,168 hours in the final quarter of 2012.
- Test MAE 45.27, RMSE 72.97, and
  R-squared 0.869.

These are associations and predictions from non-randomized observational data;
they do not establish causal effects.
