# Didactic guide to the simplified analysis

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
2. **Prediction:** can these factors predict demand in future periods?

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
| Factors | Hour, working day, weather, season, and year |
| Covariates | Temperature, humidity, and wind speed |
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
- `atemp`: it correlates 0.988 with `temp`; using both produces VIF values above
  43. We retained only `temp` to avoid multicollinearity.
- `instant`: it is only a sequential row identifier.

### Weather grouping

The original `weathersit` factor has four levels, but level 4 appears only three
times. There is not enough information for a stable separate estimate.

For inference, we use:

1. clear or partly cloudy;
2. mist or cloudy;
3. precipitation or adverse, combining original levels 3 and 4.

The raw file remains unchanged. `src/bike_sharing/data.py` creates the grouped
variable in memory.

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

Observed weather means are:

| Weather | Mean rentals/hour |
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
Y_1 = cnt, \qquad Y_2 = \sqrt{cnt}, \qquad
Y_3 = \log(1+cnt).
\]

Adding 1 keeps the logarithm defined if a zero count appears in another dataset.

### Evidence for the choice

For the M1 structure:

| Response | Shapiro--Wilk \(W\) | Breusch--Pagan | Adjusted \(R^2\) |
|---|---:|---:|---:|
| `cnt` | 0.972 | 4282.8 | 0.812 |
| `sqrt(cnt)` | 0.984 | 2039.7 | 0.893 |
| `log1p(cnt)` | 0.949 | 1672.5 | 0.927 |

The \(p\)-values from Shapiro--Wilk and Breusch--Pagan were below 0.001 on all
three scales. We selected `log1p(cnt)` because it had the best fit and the least
relative heteroscedasticity. Shapiro--Wilk alone would favour `sqrt(cnt)`, so the
choice of the log scale is a variance-and-fit compromise, not a normality pass.

Jarque--Bera, Levene, Box--Cox, and Durbin--Watson can still be computed from the
artifacts in `outputs/tables/`, but they are not part of the paper's main
narrative. With more than 17,000 observations, tests such as Shapiro--Wilk detect
even small deviations. We therefore consider tests, plots, and deviation
magnitude together.

## 6. Main effect and interaction

A **main effect** describes how the mean changes across a factor's levels. In
this observational study, we use association language.

An **interaction** occurs when one factor's behavior depends on another factor's
level. Our central case is:

\[
\text{hour} \times \text{working day}.
\]

In `outputs/figures/primary_interaction.png`:

- working days peak near 08:00 and 17:00--18:00;
- non-working days have a broader midday profile;
- the lines are not parallel and cross.

The overall working-day mean is therefore not enough. Working-day status must be
interpreted jointly with hour.

## 7. The two explanatory models

### M0: additive model

```text
log1p(cnt) ~ hour + workingday + weather + season
           + temp + humidity + windspeed + year
```

M0 assumes that the hourly shape is the same for working and non-working days.
Working-day status could only shift the whole curve up or down.

### M1: primary interaction model

```text
log1p(cnt) ~ hour * workingday + weather + season
           + temp + humidity + windspeed + year
```

In a model formula, `hour * workingday` expands to:

```text
hour + workingday + hour:workingday
```

This follows the **hierarchy principle**: when an interaction is present, its
component main effects remain in the model.

### Why treat hour as categorical?

Treating hour as one linear number would force a straight-line change from 00:00
to 23:00. The actual pattern contains an overnight trough, two working-day peaks,
and subsequent declines. We therefore use 24 categorical levels.

This creates more coefficients. M1 has 57 parameters, but the interaction curve
is more useful than listing every indicator coefficient.

## 8. ANOVA and effect size

ANOVA partitions response variation among model terms and residual error.

- **F:** compares variation attributed to a term with residual variation.
- **p-value:** measures incompatibility with a null hypothesis under the test
  assumptions.
- **Partial eta-squared:** describes the relative variation attributed to a term
  after accounting for model error.

Central M1 results:

| Term | F | p-value | Partial eta-squared |
|---|---:|---:|---:|
| Hour | 5416.44 | < 0.001 | 0.878 |
| Working day | 12.27 | < 0.001 | 0.001 |
| Hour × working day | 1079.55 | < 0.001 | 0.589 |
| Weather | 1180.12 | < 0.001 | 0.120 |
| Season | 1163.90 | < 0.001 | 0.168 |

Working day's p-value is small, but its main-effect size is much smaller than the
interaction. This illustrates why “significant” versus “not significant” is not
enough for interpretation.

## 9. Comparing M0 and M1

| Model | Parameters | Adjusted \(R^2\) | AIC | BIC |
|---|---:|---:|---:|---:|
| M0 | 34 | 0.824 | 31323.3 | 31587.2 |
| M1 | 57 | 0.927 | 15914.2 | 16356.7 |

- **Adjusted \(R^2\)** rewards explained variation while partly penalizing added
  parameters.
- **AIC** and **BIC** balance fit and complexity; lower values are preferred when
  models use the same response and observations.
- The nested F test for adding the interaction produced \(F=1079.55\) and
  \(p<0.001\).

All three criteria favor M1. More importantly, the improvement has a clear
behavioral explanation: commuting produces a distinct hourly profile.

## 10. Model diagnostics

### Residuals versus fitted

This plot checks functional form and constant variance. A funnel shape suggests
heteroscedasticity.

### Q--Q plot

This plot compares residual quantiles with normal quantiles. Tail deviations
indicate non-normal residual tails.

### VIF

The Variance Inflation Factor measures how predictor correlation inflates a
coefficient's variance. Removing `atemp` reduced the selected numerical VIF
values to approximately 1.1 or less.

### ACF and temporal dependence

The residual autocorrelation function (ACF) for M1 is:

- lag 1: 0.612;
- lag 24: 0.243;
- lag 168: 0.200.

Durbin--Watson remains available in the generated artifacts; in the main
narrative the ACF summarizes dependence across several time scales more
informatively. These are **observed-hour** lags because the calendar contains
gaps.

### Why use HAC?

HAC means *heteroskedasticity and autocorrelation consistent*. Newey--West
recalculates standard errors and confidence intervals while allowing
heteroscedasticity and temporal dependence up to a specified lag.

We use 168 observed-hour lags, approximately one week. HAC does not change model
coefficients or predictions; it changes uncertainty estimates. It also does not
eliminate every temporal limitation.

## 11. Predictive validation

A random split would allow future observations to help predict the past. We
instead use expanding temporal windows:

1. train through March 2012, validate on Q2 2012;
2. train through June 2012, validate on Q3 2012;
3. train through September 2012, test once on Q4 2012.

The final period was not used for model choice.

We compare:

- **Baseline:** historical mean for each hour and day type;
- **P0:** predictive additive counterpart of M0;
- **P1:** predictive model containing `hour × workingday`.

Predictive models replace categorical year with a continuous time index. A
“2012” category cannot represent an unseen future year, while a time index can
represent trend.

Predictions fitted on `log1p(cnt)` return to the count scale with Duan's smearing
correction. Simply calculating `exp(prediction) - 1` would be biased because the
exponential of a mean is not the mean of the exponential.

### Metrics

- **MAE:** average absolute error in rentals.
- **RMSE:** gives more weight to large errors.
- **Out-of-sample \(R^2\):** compares the model with the test-period mean.
- **RMSLE:** measures error on the logarithmic scale and reduces the dominance of
  the largest counts.

### Final Q4 2012 holdout

| Model | MAE | RMSE | \(R^2\) | RMSLE |
|---|---:|---:|---:|---:|
| Baseline | 79.95 | 119.59 | 0.648 | 0.604 |
| P0 | 85.65 | 121.25 | 0.638 | 0.725 |
| P1 | 51.99 | 83.07 | 0.830 | 0.524 |

P1 outperforms both the additive model and the baseline. The interaction is not
only statistically detectable; it also improves future prediction.

## 12. What can we conclude?

1. Hour is the main observed demand factor.
2. Its behavior strongly depends on working-day status.
3. Weather and season show important demand associations.
4. M1 represents the data better than M0.
5. The same interaction improves temporal prediction.
6. Associations do not establish causality.
7. Residual dependence remains after adjustment.

## 13. How is the code organized?

| File | Purpose |
|---|---|
| `analysis/00_validate_data.py` | Checks integrity, types, ranges, and gaps |
| `analysis/01_descriptive_analysis.py` | Creates summaries, histograms, boxplots, and correlations |
| `analysis/02_doe_analysis.py` | Creates effects, primary interaction, ANOVA, and Tukey |
| `analysis/03_assumptions_transformations.py` | Compares scales and diagnoses assumptions |
| `analysis/04_regression_models.py` | Compares M0/M1 and creates HAC/diagnostics |
| `analysis/05_temporal_validation.py` | Evaluates baseline, P0, and P1 over time |
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

## 14. Review questions before the presentation

1. Why can this study not support causal conclusions?
2. What is the difference among a factor, level, covariate, and response?
3. Why should `workingday` not be interpreted without `hr`?
4. What does the interaction add to M0?
5. Why is normality evaluated on residuals rather than the raw response?
6. Why did we remove `atemp`?
7. What does HAC correct, and what does it not correct?
8. Why is temporal splitting preferable to random splitting here?
9. How do explanatory and predictive objectives differ?
10. Why does a small p-value not guarantee practical importance?
