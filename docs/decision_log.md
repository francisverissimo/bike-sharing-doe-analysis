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

## 2026-11-20 — Reduce the final narrative to M0 versus M1

**Question:** Is the five-model MVP appropriately sized for the assignment and
for a clear oral explanation?

**Evidence:** M1 already reaches adjusted R-squared 0.927, and the primary
`hour × working day` interaction has a clear behavioral interpretation. M2--M4
add 116 parameters and several secondary questions, making the paper harder to
teach and defend.

**Decision:** The final narrative compares only additive M0 with interaction M1.
It retains descriptive analysis, transformation evidence, ANOVA/effect size,
HAC uncertainty, and chronological prediction. Secondary interactions and the
quadratic-temperature model are removed from the active pipeline but remain in
Git history.

**Consequence:** M1 is both the explanatory model and the structural basis for
P1. The simplified P1 holdout results are MAE 51.99, RMSE 83.07, R-squared 0.830,
and RMSLE 0.524. This small predictive reduction is accepted in exchange for a
substantial improvement in clarity and parsimony.

## 2026-11-20 — Maintain bilingual learning documentation

**Question:** How can both authors review statistical concepts while following
the implementation?

**Decision:** Maintain equivalent didactic guides in Brazilian Portuguese and
English. The submission article remains in English, as required by the
assignment.

**Consequence:** `docs/tutorial-pt-br.md` and `docs/tutorial-en.md` explain the
design, transformation, interaction, ANOVA, regression diagnostics, HAC,
temporal validation, results, code organization, and review questions.

## 2026-11-20 — Add a Brazilian Portuguese article version

**Question:** Should the Portuguese explanation be limited to tutorials, or should
the article itself also be available in Portuguese?

**Evidence:** The authors are reviewing statistical concepts while learning how
the analysis was implemented. A Portuguese article with the same structure,
tables, figures, and results as the English draft supports that review and the
presentation without changing the scientific scope.

**Decision:** Keep `paper/main.tex` as the canonical English submission source and
add `paper/main-pt-br.tex` as an equivalent Brazilian Portuguese version. The
English abstract is retained in the Portuguese file, followed by the Portuguese
`resumo`. CI compiles both files.

**Consequence:** Both article sources must be updated together whenever a result,
table, figure, citation, or conclusion changes. This entry refines the earlier
statement that only the article would remain in English; the English file remains
canonical for submission, while the Portuguese file is a study and review aid.

## 2026-11-20 — Keep only two formal diagnostic tests in the article

**Question:** Can the diagnostics section be reduced further without weakening
the analysis?

**Evidence:** Shapiro--Wilk covers residual normality and Breusch--Pagan covers
constant residual variance. Jarque--Bera is largely redundant with Shapiro--Wilk
and the reported skewness/kurtosis; Levene is a descriptive group comparison;
Box--Cox is optional once the scale comparison is reported; Durbin--Watson only
covers first-order autocorrelation, while the residual ACF shows dependence at
several lags. With more than 17,000 observations, all formal tests reject small
deviations, so plots and effect sizes matter more than a long test list.

**Decision:** The article reports only Shapiro--Wilk and the studentized
Breusch--Pagan test for the scale comparison, plus residual ACF as the basis for
HAC(168). Jarque--Bera, Levene, Box--Cox, and Durbin--Watson remain in the
generated outputs and Git history but are removed from the main narrative.

**Consequence:** Both papers now include a compact three-row diagnostics table
and state explicitly that the log scale is a variance-and-fit compromise, not a
normality pass. The bilingual tutorials explain the omitted tests as
supplementary material.
