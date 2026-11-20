# Statistical analysis protocol

**Status:** Final analysis protocol, aligned with `paper/main.tex` and
`paper/main-pt-br.md`. Decisions and deviations are recorded in
`docs/decision_log.md`.

## Research question

How do temporal and meteorological factors, particularly hour of day and working
day status, relate to hourly bike rental demand, and how accurately can those
factors predict demand in a later period?

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
- `weathersit` (four original categories);
- `season` (categorical).

Numerical covariates:

- `temp`;
- `hum`;
- `windspeed`;
- `yr` as a categorical factor.

`atemp` is not used because it correlates 0.988 with `temp`.

## Prespecified hypotheses

1. Mean hourly demand differs across hours of the day.
2. Working-day status changes the shape of the hourly demand profile.
3. Adverse weather is associated with lower hourly demand.
4. Temperature is associated with demand after adjustment for the factors.

The single interaction is `hr × workingday`. The hierarchy principle keeps both
component main effects in the model.

## Descriptive analysis

The analysis reports sample sizes, missingness, frequencies, mean, median,
standard deviation, quartiles, minimum, maximum, distributions, boxplots, a daily
time plot, group means with 95% confidence intervals, and numerical correlations.

## Factorial analysis of variance

A type-II factorial ANOVA is fitted by ordinary least squares on `log1p(cnt)`
with all four factors, the three covariates, year, and the `hr × workingday`
interaction. Partial eta-squared is reported for each term. Because the sample is
large and the design is observational and unbalanced, conclusions consider effect
magnitude and temporal validation rather than p-values alone. No causal
interpretation is made.

## Response scale

The response scales `cnt` and `log1p(cnt)` are compared on the same model
structure. Residual-versus-fitted plots, normal Q--Q plots, Shapiro--Wilk on a
fixed subset of 5,000 residuals, the studentized Breusch--Pagan test, and the
residual autocorrelation function guide the choice of scale.

## Regression and residual diagnostics

One regression model is specified:

```text
log1p(cnt) ~ C(hr) * C(workingday) + C(weathersit) + C(season)
             + temp + hum + windspeed + C(yr)
```

Basic residual diagnostics are residual-versus-fitted plots, normal Q--Q plots,
and the residual ACF at observed-hour lags. Duan's smearing correction is used to
return log-scale predictions to the count scale.

## Predictive validation

Random train/test splitting is not used because it would mix future and past
observations. The model is trained on all hours through 30 September 2012 and
tested on 1 October through 31 December 2012. Both years appear in the training
data so that `yr` is estimable.

Test performance is reported with MAE, RMSE, and out-of-sample R-squared on the
count scale.

## Decision criteria

The response scale is chosen by adjusted R-squared and the Breusch--Pagan
statistic, with Shapiro--Wilk and residual plots read alongside them. The final
model is fixed by the proposal's factor structure and the prespecified
interaction; no model search is performed.
