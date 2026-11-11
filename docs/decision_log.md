# Decision log

This file records decisions that affect scientific interpretation,
reproducibility, or collaboration. New entries should be appended; existing
entries should not be silently rewritten after results are known.

## 2026-10-18 — Use the hourly dataset

**Question:** Which aggregation should be analyzed?

**Evidence:** `hour.csv` contains 17,379 observations and includes hour of day,
whereas `day.csv` contains 731 daily observations and cannot represent hourly
commuting patterns.

**Decision:** Use `dataset/hour.csv` for all primary analyses. Retain `day.csv`
only as part of the original distribution.

**Consequence:** Hour of day can be modeled as a factor and interacted with
working-day status.

## 2026-10-18 — Treat the study as observational

**Question:** How should the experimental design be described?

**Evidence:** Weather and calendar conditions were observed during normal system
operation; researchers did not assign or randomize treatments.

**Decision:** Describe the data as observational with a natural factorial and
temporal structure.

**Consequence:** Report associations rather than causal effects and explicitly
evaluate temporal dependence.

## 2026-10-18 — Prioritize the working-day by hour interaction

**Question:** Which interaction should anchor the DOE analysis?

**Evidence:** Commuting behavior predicts morning and evening peaks on working
days and a different recreational profile on other days.

**Decision:** Prespecify `workingday × hr` as the primary interaction.

**Consequence:** Both main effects remain in every model containing the
interaction.

## 2026-10-30 — Use Python scripts as the implementation

**Question:** Which language and executable format should be canonical?

**Decision:** Use Python 3.10 and standalone scripts, without notebooks.

**Consequence:** Reusable logic belongs in `src/bike_sharing/`, and numbered
scripts under `analysis/` generate deterministic outputs.

## 2026-10-30 — Collaborate directly on the main branch

**Question:** How should the pair integrate work?

**Decision:** Both contributors commit directly to `main`.

**Consequence:** Contributors must coordinate file ownership, synchronize before
pushing, never force-push, and keep every shared commit complete and tested.

## 2026-10-30 — Publish a public GitHub repository

**Question:** Where should the project be hosted?

**Decision:** Publish the project as `bike-sharing-doe-analysis` on GitHub and
retain the assignment and UCI screenshots in the public history.

**Consequence:** Dataset attribution and public-file review are required before
the first push.

## 2026-11-04 — Do not license original project material yet

**Question:** Which license should apply to code and original text?

**Decision:** Grant no code or text license at this stage. Continue to respect
the dataset's CC BY 4.0 license and attribution requirements.

**Consequence:** No repository-level `LICENSE` file will be created until both
authors make a later explicit decision.

## 2026-11-04 — Separate inference from prediction

**Question:** Should one fitted model serve both statistical interpretation and
future prediction?

**Evidence:** Full-sample inference and chronological predictive evaluation have
different goals and leakage constraints. A 2011-only training set also cannot
estimate a categorical 2012 year effect.

**Decision:** Maintain an explanatory analysis for effects and interactions and
a separate chronologically evaluated predictive workflow.

**Consequence:** Prediction will use expanding windows and an end-of-2012
holdout rather than a random split or a strict 2011/2012 split with `yr` as an
unseen categorical level.

## 2026-11-11 — Combine sparse severe weather with precipitation

**Question:** How should weather level 4 be represented in inferential models?

**Evidence:** Only 3 of 17,379 observations have `weathersit = 4`, compared with
1,419 at level 3. A separate level-4 coefficient would be unstable and could not
support meaningful contrasts.

**Decision:** Preserve the original four-level variable for provenance and
descriptive counts, but combine levels 3 and 4 into
`Precipitation/adverse` for models and effect plots.

**Consequence:** The grouped category has 1,422 observations. Conclusions do not
claim to estimate severe-weather demand separately.

## 2026-11-11 — Do not impute absent hourly timestamps

**Question:** Should the 165 gaps in the hourly calendar sequence be imputed?

**Evidence:** The response is available for 17,379 observed hours, and the MVP
models use contemporaneous factors rather than lagged response values. An
unobserved record cannot be assumed to represent zero rentals.

**Decision:** Analyze recorded hours only and report the 165 absent timestamps.

**Consequence:** Residual ACF lags are described as observed-hour lags rather
than exact clock-hour lags around gaps.

## 2026-11-11 — Exclude apparent temperature

**Question:** Should `temp` and `atemp` be included together?

**Evidence:** Their Pearson correlation is 0.988. Their candidate-set VIF values
are 43.55 and 43.65; after removing `atemp`, selected numeric VIF values are near
1.1 or below.

**Decision:** Retain `temp` and exclude `atemp` from explanatory and predictive
models.

**Consequence:** Thermal effects are represented by normalized temperature and
its quadratic term without unstable duplicate information.

## 2026-11-11 — Use log-one-plus count as the MVP response scale

**Question:** Which response scale should anchor linear regression?

**Evidence:** For the M1 structure, adjusted R-squared was 0.812 for raw `cnt`,
0.893 for `sqrt(cnt)`, and 0.927 for `log1p(cnt)`. The Breusch--Pagan statistic
decreased from 4282.8 to 2039.7 and 1672.5, respectively. Box--Cox estimated
lambda 0.305. No candidate fully satisfied normality, homoscedasticity, and
independence.

**Decision:** Use `log1p(cnt)` for the MVP because it provides the best variance
stabilization among the prespecified simple transformations, supports
multiplicative interpretation, and works with smearing back-transformation.

**Consequence:** Continue to report residual violations and use HAC uncertainty;
do not present the transform as a complete cure.

## 2026-11-11 — Use HAC with 168 observed-hour lags

**Question:** How should uncertainty account for residual temporal dependence?

**Evidence:** In the final explanatory model, Durbin--Watson is 0.861. In the M1
log model, residual ACF is 0.612 at lag 1, 0.243 at lag 24, and 0.200 at lag 168.

**Decision:** Report Newey--West HAC coefficient intervals with `maxlags=168`
for the full explanatory model.

**Consequence:** Classical ANOVA remains a descriptive decomposition, while
coefficient-level inference includes a one-week observed-hour dependence window.

## 2026-11-11 — Distinguish the full explanatory model from the predictor

**Question:** Which model should represent explanation and which should predict?

**Evidence:** M4, including hour interactions and quadratic temperature, had the
lowest explanatory BIC (15531.4) and adjusted R-squared 0.935. For chronological
prediction, P1 had the lowest mean validation RMSE (101.51); adding weather by
hour increased it to 102.86.

**Decision:** Use M4 as the full MVP explanatory model and P1, containing the
primary hour by working-day interaction, as the selected predictive model.

**Consequence:** On the untouched Q4 2012 holdout, P1 achieved MAE 50.18, RMSE
81.65, out-of-sample R-squared 0.836, and RMSLE 0.501. In-sample significance is
not used as the sole criterion for predictive complexity.
