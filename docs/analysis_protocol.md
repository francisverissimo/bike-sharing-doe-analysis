# Statistical analysis protocol

**Status:** Frozen for the MVP on 2026-11-11. The core hypotheses and methods
were committed before result generation; implementation decisions and deviations
are recorded in `docs/decision_log.md`.

## Research question

How do temporal and meteorological factors, particularly hour of day and working
day status, relate to hourly bike rental demand, and how accurately can those
factors predict future hourly demand?

## Study design

This is an observational study with a natural factorial structure. There was no
controlled assignment or randomization. Each record represents one observed
hour, and the records are sequential in time. Results support association and
prediction, not causal claims.

## Response

`cnt`, the total number of rentals in an hour.

`casual` and `registered` are excluded from all predictor sets because their sum
equals `cnt`.

## Factors and covariates

Primary factors:

- `hr` (categorical, 24 levels);
- `workingday` (binary);
- `weathersit` (ordinal categories);
- `season` (categorical).

Primary numerical covariates:

- `temp`;
- `hum`;
- `windspeed`.

`atemp` will not initially accompany `temp` because the two variables measure
closely related thermal conditions. `mnth` and `season` will not be included
together without a specific justification.

## Prespecified hypotheses

1. Mean hourly demand differs across hours of the day.
2. Working-day status changes the shape of the hourly demand profile.
3. Adverse weather is associated with lower hourly demand.
4. Temperature has a potentially nonlinear association with demand.

The primary interaction is `workingday × hr`. Secondary, exploratory
interactions are `weathersit × hr`, `season × hr`, and
`workingday × weathersit`.

## Descriptive analysis

The analysis will report sample sizes, missingness, frequencies, mean, median,
standard deviation, quartiles, minimum, maximum, distributions, boxplots, time
plots, group means with uncertainty intervals, and numerical correlations.

## Inferential analysis

Main effects and interactions will be examined through effect plots, factorial
ANOVA/ANCOVA, nested-model comparisons, confidence intervals, and effect sizes.
Tukey HSD will be used for prespecified pairwise comparisons only when its
assumptions are defensible. The hierarchy principle requires main effects to
remain whenever their interaction is present.

Because the sample is large, conclusions will not rely on p-values alone. They
will also consider effect magnitude, confidence intervals, practical relevance,
and temporal stability. Statistical associations will not be described as
causal effects.

## Assumptions and transformations

Candidate response scales are `cnt`, `sqrt(cnt)`, and `log1p(cnt)`. Residual
normality, variance stability, functional form, influential observations, and
temporal autocorrelation will guide the decision. Diagnostics include QQ-plots,
residual-versus-fitted and scale-location plots, Levene-type tests,
Durbin–Watson, ACF/PACF, VIF, Cook's distance, leverage, and studentized
residuals.

Classical standard errors will be compared with a temporal adjustment, such as
HAC/Newey–West or clustering by date. The final choice will be recorded after
inspecting residual autocorrelation.

## Explanatory models

Models will be developed hierarchically:

1. main effects;
2. add `workingday × hr`;
3. evaluate secondary interactions one at a time;
4. evaluate a quadratic temperature term;
5. select a parsimonious, interpretable final model.

A negative-binomial regression may be included as a sensitivity analysis if the
linear models remain unsuitable for the count response after transformation.

## Predictive validation

Random train/test splitting is prohibited. Validation will preserve chronology
using expanding windows and a final holdout from the end of 2012. No observation
may be used to predict an earlier observation.

Prediction will be assessed with MAE, RMSE, out-of-sample R-squared, and, if it
adds useful information, RMSLE. Models will be compared with a simple baseline
such as the historical mean for each `hr × workingday` combination.

For explanatory analysis, `yr` may be categorical. Predictive models may instead
use a continuous time index so that temporal growth is representable beyond an
observed year category.

## Decision criteria

The final model will balance assumption compliance, adjusted R-squared, AIC/BIC,
chronological validation performance, interpretability, hierarchy, and
parsimony. No observation or model term will be removed solely to improve a
reported metric.
