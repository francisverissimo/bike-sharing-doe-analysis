# Statistical analysis protocol

**Status:** Final analysis protocol. The methodological decisions that define
this analysis are recorded in `docs/decision_log.md`.

## Research question

How do temporal and meteorological factors, particularly hour of day and working
day status, relate to hourly bike rental demand, and how accurately can those
factors predict demand in the following calendar year?

## Study design

This is an observational study with a natural factorial structure. There was no
controlled assignment or randomization. Each record represents one observed hour,
and the records are sequential in time. Results support association and
prediction, not causal claims.

## Response

`cnt`, the total number of rentals in an hour.

`casual` and `registered` are excluded because their sum equals `cnt`.

## Factors and covariates

Primary factors:

- `hr` (categorical, 24 levels);
- `workingday` (binary);
- `weathersit` (levels 3 and 4 pooled into one precipitation/adverse condition;
  the raw four-level variable is retained for data validation);
- `season` (categorical).

Numerical covariates:

- `temp`;
- `hum`;
- `windspeed`.

`atemp` is not used because it correlates 0.988 with `temp`. The year indicator
is not a regressor: with training restricted to 2011, it has no variation. It
remains available for descriptive time-series context.

## Prespecified hypotheses and interactions

1. Mean hourly demand differs across hours of the day.
2. Working-day status changes the shape of the hourly demand profile.
3. Pooled adverse weather is associated with lower hourly demand.
4. Temperature is associated with demand after adjustment for the factors.

Three hour interactions are examined: `hr × workingday`, `hr × weather_group`,
and `hr × season`. The hierarchy principle keeps component main effects whenever
an interaction is retained. The final selected model retains only
`hr × workingday` because BIC penalises the additional interaction terms.

## Descriptive analysis

The analysis reports sample sizes, missingness, frequencies, mean, median,
standard deviation, quartiles, minimum, maximum, distributions, boxplots, a daily
time plot, group means with 95% confidence intervals, and numerical correlations.
Main-effect plots cover the four factors; interaction plots cover the three
prespecified hour interactions.

## One-way analysis of variance

Separate one-way ANOVAs on `log1p(cnt)` quantify the marginal association of each
of the four factors with the response. Both $\eta^2$ and $\omega^2$ are reported
because the training sample has 8,645 observations and p-values alone are
uninformative. Working day is interpreted jointly with hour because its marginal
effect is negligible.

## Factorial analysis of variance

A type-II factorial ANOVA is fitted by ordinary least squares on the 2011
training data. The final model contains all four factors, the three continuous
covariates, and the `hr × workingday` interaction. Partial eta-squared is
reported for every term. Because the sample is large and the design is
observational and unbalanced, conclusions consider effect magnitude and temporal
validation rather than p-values alone. No causal interpretation is made.

## Post-hoc weather comparisons

Because the omnibus weather effect is significant, Tukey's honestly significant
difference (HSD) procedure compares the three pooled weather conditions on
`log1p(cnt)`. It controls the family-wise error rate across the three pairwise
contrasts and reports simultaneous 95% confidence intervals. No separate contrast
is attempted for the three severe-weather hours.

## Progressive model sequence

Four nested candidates are fitted on the same 2011 training sample:

```text
M0: log1p(cnt) ~ C(hr) + C(workingday) + C(weather_group) + C(season)
                 + temp + hum + windspeed
M1: M0 + C(hr):C(workingday)
M2: M1 + C(hr):C(weather_group) + C(hr):C(season)
M3: M2 + I(temp**2)
```

Candidates are compared by adjusted R-squared, AIC, BIC, and nested F tests. The
candidate with the lowest training BIC is retained as the final M4. Selection
uses training data only. BIC selects M1, so M4 has 56 parameters.

## Response scales

Four response scales are evaluated on the selected model structure: `cnt`,
`sqrt(cnt)`, `log1p(cnt)`, and a Box--Cox transformation with its exponent
estimated from training counts. The comparison uses residual-versus-fitted
plots, normal Q--Q plots, Shapiro--Wilk on a deterministic subset of 5,000
residuals, the studentized Breusch--Pagan test, adjusted R-squared, and held-out
count-scale MAE, RMSE, and R-squared. `log1p(cnt)` is retained for the best
combination of accuracy and interpretability, not as a claim of normal residuals.

## Residual diagnostics

For the retained scale, the full diagnostic checklist includes:

- residual-versus-fitted and normal Q--Q plots;
- Shapiro--Wilk and studentized Breusch--Pagan tests;
- Levene and Bartlett tests across fitted-value quintiles;
- Durbin--Watson, residual ACF and PACF at observed-hour lags;
- variance inflation factors for all non-intercept coefficients;
- leverage and Cook's distance.

Duan's smearing correction is used to return log-scale predictions to the count
scale. Scale-specific smearing is also used when evaluating the other candidate
responses.

## Predictive validation

Random train/test splitting is not used because it would mix future and past
observations. The model is trained on all 8,645 hours of 2011 and tested on all
8,734 hours of 2012. Because the year indicator cannot be estimated from a single
training year, the test error also reflects unmodelled system growth.

Test performance is reported with MAE, RMSE, and out-of-sample R-squared on the
count scale. Final test metrics are MAE 87.67, RMSE 125.19, and R-squared 0.641.

## Decision criteria

The final model is selected by training BIC, with hierarchy enforced. Held-out
accuracy selects the response scale among the four candidates. Diagnostics are
reported in full rather than used to advertise a normality pass: temporal
dependence and heteroscedasticity remain, so inferential p-values are descriptive
and the chronological test set is the main predictive evidence.
