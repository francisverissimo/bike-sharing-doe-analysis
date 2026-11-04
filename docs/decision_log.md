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
