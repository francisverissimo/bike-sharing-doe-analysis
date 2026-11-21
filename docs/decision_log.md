# Decision log

This file records the methodological decisions that define the current analysis.
Each entry states the decision and its consequence for interpretation or
reproducibility.

## Analyze the hourly dataset

**Question:** Which aggregation should be analyzed?

**Evidence:** `hour.csv` contains 17,379 observations and includes hour of day,
whereas `day.csv` contains 731 daily observations and cannot represent hourly
commuting patterns.

**Decision:** Use `dataset/hour.csv` for all analyses. Retain `day.csv` only as
part of the original distribution.

**Consequence:** Hour is modeled as a 24-level factor and interacted with other
factors.

## Treat the study as observational

**Question:** How should the design be described?

**Evidence:** Weather and calendar conditions were observed during normal system
operation; treatments were not assigned or randomized.

**Decision:** Describe the data as observational with a natural factorial and
temporal structure.

**Consequence:** Report associations and predictions rather than causal effects,
and evaluate temporal dependence explicitly.

## Prespecify three hour interactions

**Question:** Which interactions should the DOE analysis examine?

**Evidence:** Commuting behavior predicts different working-day and non-working-day
hourly profiles; weather and season may also modify the hourly pattern.

**Decision:** Examine `hr × workingday`, `hr × weather_group`, and `hr × season`.
Treat `hr × workingday` as the primary interaction and keep component main
effects whenever an interaction is retained.

**Consequence:** The final model retains only `hr × workingday` because BIC
penalises the additional terms; all three interactions are still plotted and
tested in the model sequence.

## Use executable Python scripts

**Question:** Which implementation format should be canonical?

**Decision:** Use Python 3.10 with numbered scripts under `analysis/` and reusable
modules under `src/bike_sharing/`.

**Consequence:** `make all` regenerates deterministic outputs; no notebooks are
required to reproduce the analysis.

## Use a strict chronological split

**Question:** How should training and test data be separated?

**Evidence:** Random splitting would mix future and past observations. Training
only on 2011 leaves the year indicator constant in training.

**Decision:** Train on all 8,645 hours of 2011 and test on all 8,734 hours of 2012.
Use `yr` for descriptive time-series context only, never as a regressor.

**Consequence:** Test error includes unmodelled system growth between years. The
chronological test set is the main predictive evidence.

## Pool sparse severe weather with precipitation

**Question:** How should weather level 4 be represented in models?

**Evidence:** Only 3 of 17,379 observations have `weathersit = 4`, against 1,419 at
level 3. A separate level-4 coefficient would be unstable and could not support
meaningful contrasts.

**Decision:** Keep the original four-level variable for validation and descriptive
counts, but combine levels 3 and 4 into one precipitation/adverse condition for
models and effect plots.

**Consequence:** The grouped category has 1,422 observations. No conclusion claims
to estimate severe-weather demand separately.

## Do not impute absent hourly timestamps

**Question:** Should the 165 gaps in the hourly calendar be imputed?

**Evidence:** The response is available for 17,379 recorded hours, and the models
use contemporaneous factors rather than lagged response values. An unobserved
record cannot be assumed to have zero rentals.

**Decision:** Analyze recorded hours only and report the 165 absent timestamps.

**Consequence:** Autocorrelation lags are described as observed-hour lags rather
than exact clock-hour lags.

## Exclude apparent temperature

**Question:** Should `temp` and `atemp` be included together?

**Evidence:** Their Pearson correlation is 0.988. Their candidate-set VIF values
are 43.55 and 43.65; after removing `atemp`, selected numeric VIF values are near
1.1 or below.

**Decision:** Retain `temp` and exclude `atemp`. Include `I(temp**2)` in M3 to
represent a non-linear thermal effect.

**Consequence:** Temperature is represented without unstable duplicate
information.

## Use log-one-plus count as the response

**Question:** Which response scale should anchor regression?

**Evidence:** For the selected structure, adjusted R-squared favours `log1p(cnt)`;
the estimated Box–Cox exponent is 0.315, and `log1p(cnt)` has the best held-out
count-scale accuracy. No candidate satisfies normality or homoscedasticity.

**Decision:** Fit and report models on `log1p(cnt)`, and use Duan's smearing
correction when returning predictions to the count scale.

**Consequence:** The transformation is a variance-and-fit compromise, not a claim
of normal residuals.

## Select M4 by training-only BIC

**Question:** How should the progressive model sequence be resolved?

**Evidence:** M0–M3 are nested candidates fitted on the same 2011 sample. M2 and
M3 add 115 and 116 parameters and have higher BIC (9103.7 and 8786.0) than M1
(8673.5).

**Decision:** Compare M0–M3 by adjusted R-squared, AIC, BIC and nested F tests on
training data only; retain the lowest-BIC candidate as M4.

**Consequence:** BIC selects M1, so M4 = M1 with 56 parameters, adjusted
R-squared 0.920, AIC 8277.9, and BIC 8673.5.

## Report one-way ANOVA and Tukey contrasts

**Question:** How should factor effects be summarized?

**Decision:** Report separate one-way ANOVAs on `log1p(cnt)` for all four factors,
a type-II factorial ANOVA on the final structure, and Tukey HSD for the three
pooled weather conditions.

**Consequence:** Hour has one-way eta-squared 0.695; factorial partial
eta-squared is 0.866 for hour and 0.569 for hour by working day. All three
adjusted weather contrasts are significant. Effect sizes are emphasised because
p-values are uninformative with this sample size.

## Compare four response scales

**Question:** Should the response scale be assumed or evaluated?

**Decision:** Evaluate `cnt`, `sqrt(cnt)`, `log1p(cnt)` and Box–Cox on the selected
structure using residual plots, formal diagnostics, adjusted R-squared and 2012
accuracy.

**Consequence:** `log1p(cnt)` is retained for the best combination of accuracy and
interpretability; the other scales and the Box–Cox exponent remain reported.

## Report the full diagnostic checklist

**Question:** How thoroughly should model assumptions be reported?

**Decision:** Report residual-versus-fitted and Q–Q plots, Shapiro–Wilk,
studentized Breusch–Pagan, Levene, Bartlett, Durbin–Watson, ACF and PACF at
observed-hour lags, VIF, leverage and Cook's distance.

**Consequence:** Shapiro–Wilk is 0.959, Breusch–Pagan 854.0, and Durbin–Watson
0.814; ACF at lags 1/24/168 is 0.593/0.201/0.138. Heteroscedasticity and temporal
dependence remain, so inferential p-values are descriptive. Maximum VIF is 24.0,
maximum Cook's distance 0.0067, and maximum leverage 0.0139; no observation
dominates the fit.

## Validate on the unseen year

**Question:** How should predictive accuracy be reported?

**Decision:** Fit the final structure and every response scale on 2011 only, then
report MAE, RMSE and out-of-sample R-squared on 2012 counts after smearing.

**Consequence:** `log1p(cnt)` gives MAE 87.67, RMSE 125.19 and R-squared 0.641.
The result is a prediction from observational data, not a causal estimate.
