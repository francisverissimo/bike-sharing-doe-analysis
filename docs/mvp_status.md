# Simplified bilingual MVP status

## Included

- Deterministic audit of the original UCI files.
- Descriptive statistics, distributions, boxplots, time series, and correlations.
- Main-effect plots and the primary `hour × working day` interaction plot.
- One-way and factorial ANOVA, effect sizes, Tukey contrasts, and HAC tables.
- Raw, square-root, and log comparisons using Shapiro--Wilk, Breusch--Pagan,
  residual ACF, and Q--Q plots.
- The focused M0--M1 explanatory comparison and influence diagnostics.
- Expanding-window model selection and untouched Q4 2012 holdout evaluation.
- Generated report tables, SBC-format article drafts in English and Brazilian
  Portuguese, and presentation outlines in both languages.
- Automated tests, linting, and one-command reproduction through `make all`.
- Equivalent didactic guides in English and Brazilian Portuguese.

## Decisions made in the MVP

- Merge weather levels 3 and 4 for inference while preserving the raw column.
- Use `log1p(cnt)` as the primary MVP response scale.
- Remove `atemp` from models due to collinearity with `temp`.
- Use HAC(168) uncertainty for the full explanatory model.
- Use M1 as the explanatory model and P1 as its predictive counterpart.

## Required before final submission

- Insert both authors' names, affiliations, and email addresses.
- Compile and visually inspect both `paper/main.tex` and `paper/main-pt-br.tex`
  in an SBC-compatible LaTeX environment.
- Confirm that the paper remains within 6–12 pages and reduce tables if necessary.
- Keep individual HAC coefficients, influential observations, Jarque--Bera,
  Levene, Box--Cox, and Durbin--Watson as supplementary evidence rather than
  article-body material.
- Keep nonlinear, secondary-interaction, count, and autoregressive models outside
  the final scope unless the professor explicitly requests them.
- Have both authors independently reproduce `make all` from a clean clone.
- Create the final slides, proofread the English, and tag the submitted release.
