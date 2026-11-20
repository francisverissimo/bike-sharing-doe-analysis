# Didactic guide to the analysis

This document explains the work step by step. Its purpose is not only to present
results, but also to review the statistical concepts and connect each concept to
the project code.

An equivalent Brazilian Portuguese version is available in
[`tutorial-pt-br.md`](tutorial-pt-br.md).

## 1. What is the research question?

We answer two related but distinct questions:

1. **Explanation:** which factors are associated with hourly bicycle demand and,
   in particular, does the effect of hour differ between working and non-working
   days?
2. **Prediction:** can these factors predict demand in a later period?

The response is `cnt`, the total number of bicycles rented during an hour.

## 2. Why is this an observational study?

In a controlled experiment, researchers choose treatments and randomly assign
them to experimental units. That did not happen here. The records came from the
real operation of Capital Bikeshare.

- Nobody randomly assigned rainy days.
- Nobody randomized which hours belonged to working days.
- Season, temperature, and humidity occurred naturally.

This is therefore an **observational study with a natural factorial structure**.
We can describe associations, but we cannot claim that one variable caused
another.

### Design terminology

| Concept | Application in this study |
|---|---|
| Observational unit | One recorded hour on a given date |
| Response | `cnt`, total rentals in that hour |
| Factors | Hour, working-day status, pooled weather condition, season |
| Covariates | Temperature, humidity, wind speed |
| Levels | For example, `workingday` has levels 0 and 1 |
| Randomization | None |
| Planned blocks | None |
| Temporal repetition | Records are sequential and correlated in time |

### Why not use OFAT?

OFAT means *one factor at a time*. It would be inadequate because the behavior
of one variable may depend on another variable.

At 08:00, a working day has high commuting demand. At 08:00 on a Sunday, the
pattern is different. This dependency is an **interaction**.

## 3. Understanding the dataset

The primary file is `dataset/hour.csv`.

- 17,379 observations;
- 731 dates from January 1, 2011 through December 31, 2012;
- `cnt` ranges from 1 to 977;
- no missing cells in recorded rows;
- 165 timestamps absent from the full hourly calendar;
- `cnt = casual + registered` in every row.

The absent hours were not filled. A missing record does not imply zero rentals,
so assigning zero would introduce an unsupported assumption.

### Excluded variables

- `casual` and `registered`: they compose `cnt`. Using them to predict `cnt`
  would be **target leakage**.
- `atemp`: it correlates 0.988 with `temp`. We use only `temp` to avoid
  redundant predictors.
- `instant`: it is only a sequential row identifier.

The analysis uses four factors: `hr`, `workingday`, a pooled weather condition
from `weathersit`, and `season`. Raw level 4 occurs in only three hours, so levels
3 and 4 are combined into one precipitation/adverse condition. The raw four-level
variable is retained for data validation.

## 4. Descriptive analysis

Descriptive statistics summarize observed data without fitting an inferential
model.

| Measure | Result |
|---|---:|
| Observations | 17,379 |
| Mean | 189.46 |
| Median | 142 |
| Standard deviation | 181.39 |
| First quartile | 40 |
| Third quartile | 281 |
| Minimum | 1 |
| Maximum | 977 |

The mean exceeds the median, indicating a right-skewed distribution: many hours
have low or moderate demand, while some have very high demand.

### Reading the plots

- **Histogram:** shows the number of hours in each demand range.
- **Boxplot:** compares medians, quartiles, and extreme observations across groups.
- **Main-effects plot:** shows the response mean at each factor level.
- **Interaction plot:** shows one factor's means separately for levels of another.

Observed means for the pooled weather conditions are:

| Weather condition | Mean rentals/hour |
|---|---:|
| Clear/partly cloudy | 204.87 |
| Mist/cloudy | 175.17 |
| Precipitation/adverse | 111.50 |

These are **unadjusted** means. Part of each difference may be related to hour,
season, temperature, or other variables.

## 5. Why transform `cnt`?

Linear regression does not require the raw response itself to be normally
distributed. Among other assumptions, the **residuals** should have an adequate
distribution and approximately constant variance.

Counts are often skewed and have variance that grows with the mean. We compared:

\[
Y_1 = cnt, \qquad Y_2 = \log(1+cnt).
\]

Adding 1 keeps the logarithm defined if a zero count appears in another dataset.

### Evidence for the choice

| Response | Shapiro--Wilk \(W\) | Breusch--Pagan | Adjusted \(R^2\) |
|---|---:|---:|---:|
| `cnt` | 0.972 | 4282.8 | 0.812 |
| `log1p(cnt)` | 0.949 | 1672.5 | 0.927 |

The \(p\)-values of both tests were below 0.001 on both scales. We use
`log1p(cnt)` because it fits better and reduces the Breusch--Pagan statistic.
Shapiro--Wilk alone does not favour this scale, so the decision is a
variance-and-fit compromise, not a claim of normal residuals.

With more than 17,000 observations, formal tests detect even small deviations.
Tests, plots, and deviation magnitude are therefore read together.

## 6. Main effect and interaction

A **main effect** describes how the mean changes across a factor's levels. In
this observational study, we use association language.

An **interaction** occurs when one factor's behavior depends on another factor's
level. Our prespecified case is:

\[
\text{hour} \times \text{working day}.
\]

In `outputs/figures/workingday_hr_interaction.png`:

- working days peak near 08:00 and 17:00--18:00;
- non-working days have a broader midday profile;
- the lines are not parallel and cross.

The overall working-day mean is therefore not enough. Working-day status must be
interpreted jointly with hour.

## 7. One regression model

The model was specified once:

```text
log1p(cnt) ~ hr * workingday + weather_group + season
            + temp + hum + windspeed + yr
```

Here `weather_group` is the three-level pooled weather condition. In the
`statsmodels` formula used in the code, the categorical terms are written
`C(hr)`, `C(workingday)`, `C(weather_group)`, `C(season)`, and `C(yr)`.

In a model formula, `hr * workingday` expands to:

```text
hr + workingday + hr:workingday
```

This follows the **hierarchy principle**: when an interaction is present, its
component main effects remain in the model.

### Why treat hour as categorical?

Treating hour as one linear number would force a straight-line change from 00:00
to 23:00. The actual pattern contains an overnight trough, two working-day peaks,
and subsequent declines. We therefore use 24 categorical levels.

The model has 57 parameters because a 24-level hour factor interacts with a
binary factor and weather has three pooled levels. The interaction curve is more useful than listing every indicator
coefficient.

## 8. ANOVA and effect size

ANOVA partitions response variation among model terms and residual error.

- **F:** compares variation attributed to a term with residual variation.
- **p-value:** measures incompatibility with a null hypothesis under the test
  assumptions.
- **Partial eta-squared:** describes the relative variation attributed to a term
  after accounting for model error.

Central results:

| Term | F | p-value | Partial eta-squared |
|---|---:|---:|---:|
| Hour | 5416.44 | < 0.001 | 0.878 |
| Working day | 12.27 | < 0.001 | 0.001 |
| Weather condition | 1180.12 | < 0.001 | 0.120 |
| Season | 1163.90 | < 0.001 | 0.168 |
| Year | 6204.50 | < 0.001 | 0.264 |
| Hour × working day | 1079.55 | < 0.001 | 0.589 |

Working day's p-value is small, but its main-effect size is much smaller than the
interaction. This illustrates why “significant” versus “not significant” is not
enough for interpretation. The model has adjusted \(R^2 = 0.927\),
AIC 15914.2, and BIC 16356.7 on `log1p(cnt)`.

### Tukey HSD for weather

Because the weather ANOVA term is significant, Tukey's HSD compares the three
pooled conditions on `log1p(cnt)`. It controls the family-wise error rate across
the three pairs and gives simultaneous confidence intervals. All three contrasts
are significant after adjustment (\(p<0.001\)): clear versus mist 0.142
(95% CI 0.084 to 0.199), clear versus adverse 0.691 (0.599 to 0.784), and mist
versus adverse 0.550 (0.450 to 0.650). The adverse category is heterogeneous
because it pools two rare raw levels.

## 9. Basic residual diagnostics

### Residuals versus fitted

This plot checks functional form and constant variance. A funnel shape suggests
heteroscedasticity.

### Q--Q plot

This plot compares residual quantiles with normal quantiles. Tail deviations
indicate non-normal residual tails.

### ACF and temporal dependence

The residual autocorrelation function (ACF) is:

- lag 1: 0.612;
- lag 24: 0.243;
- lag 168: 0.200.

These are **observed-hour** lags because the calendar contains gaps. The ACF
shows that temporal dependence remains after the included factors. The ANOVA
p-values are therefore read descriptively, and the chronological test set is the
main evidence of predictive performance.

## 10. Temporal train/test split

A random split would allow future observations to help predict the past. We use
one strictly chronological division:

- **training:** all hours through 30 September 2012 (15,211 hours);
- **testing:** 1 October through 31 December 2012 (2,168 hours).

Both years appear in the training data, so the year factor is estimable.

Predictions fitted on `log1p(cnt)` return to the count scale with Duan's smearing
correction. Simply calculating `exp(prediction) - 1` would be biased because the
exponential of a mean is not the mean of the exponential.

### Metrics

- **MAE:** average absolute error in rentals.
- **RMSE:** gives more weight to large errors.
- **Out-of-sample \(R^2\):** compares the model with the test-period mean.

### Test results

| MAE | RMSE | \(R^2\) |
|---:|---:|---:|
| 45.27 | 72.97 | 0.869 |

## 11. What can we conclude?

1. Hour is the main observed demand factor.
2. Its behavior strongly depends on working-day status.
3. Weather and season show important demand associations.
4. The logarithmic scale gives the better fit and variance behaviour.
5. The model predicts an unseen quarter with \(R^2 = 0.869\).
6. Associations do not establish causality.
7. Residual dependence remains after adjustment.

## 12. How is the code organized?

| File | Purpose |
|---|---|
| `analysis/00_validate_data.py` | Checks integrity, types, ranges, and gaps |
| `analysis/01_descriptive_analysis.py` | Creates summaries, histograms, boxplots, and correlations |
| `analysis/02_doe_analysis.py` | Creates main effects, interaction plot, ANOVA, and weather Tukey HSD |
| `analysis/03_assumptions_transformations.py` | Compares response scales and basic residual diagnostics |
| `analysis/04_regression_models.py` | Fits the single regression model |
| `analysis/05_temporal_validation.py` | Evaluates the model on the chronological test set |
| `analysis/06_report_assets.py` | Creates paper tables and bilingual summaries |
| `src/bike_sharing/` | Shared functions called by the scripts |

Run the complete analysis with:

```bash
make setup
make all
```

Check the code with:

```bash
make lint
make test
```

## 13. Review questions before the presentation

1. Why can this study not support causal conclusions?
2. What is the difference among a factor, level, covariate, and response?
3. Why should `workingday` not be interpreted without `hr`?
4. How does the interaction appear in the model formula?
5. Why is normality evaluated on residuals rather than the raw response?
6. Why do we use `temp` and not `atemp`?
7. What does the residual ACF tell us?
8. Why is temporal splitting preferable to random splitting here?
9. How do explanatory and predictive objectives differ?
10. Why does a small p-value not guarantee practical importance?
11. Why are weather levels 3 and 4 pooled, and what does Tukey HSD control?
