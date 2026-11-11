# MVP status

## Included

- Deterministic audit of the original UCI files.
- Descriptive statistics, distributions, boxplots, time series, and correlations.
- Main-effect and interaction plots.
- One-way and factorial ANOVA, effect sizes, Tukey contrasts, and HAC tables.
- Raw, square-root, log, and Box--Cox diagnostic evidence.
- Hierarchical explanatory regressions and influence diagnostics.
- Expanding-window model selection and untouched Q4 2012 holdout evaluation.
- Generated report tables, an SBC-format article draft, and presentation outline.
- Automated tests, linting, and one-command reproduction through `make all`.

## Decisions made in the MVP

- Merge weather levels 3 and 4 for inference while preserving the raw column.
- Use `log1p(cnt)` as the primary MVP response scale.
- Remove `atemp` from models due to collinearity with `temp`.
- Use HAC(168) uncertainty for the full explanatory model.
- Treat M4 as the full explanatory model and P1 as the selected predictor.

## Required before final submission

- Insert both authors' names, affiliations, and email addresses.
- Compile and visually inspect `paper/main.tex` in an SBC-compatible LaTeX environment.
- Confirm that the paper remains within 6–12 pages and reduce tables if necessary.
- Review individual HAC coefficients and influential observations in the discussion.
- Consider a negative-binomial or autoregressive sensitivity model if space permits.
- Have both authors independently reproduce `make all` from a clean clone.
- Create the final slides, proofread the English, and tag the submitted release.
