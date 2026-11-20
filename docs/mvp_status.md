# Analysis status

## Included

- Deterministic audit of the original UCI hourly file.
- Descriptive statistics, distributions, boxplots, time series, and correlations
  for `cnt`.
- Main-effect plots for `hr`, `workingday`, `weathersit`, and `season`.
- One `workingday × hr` interaction plot.
- One factorial ANOVA with partial eta-squared.
- Comparison of `cnt` and `log1p(cnt)`.
- One regression model with `hr × workingday`, `weathersit`, `season`, `temp`,
  `hum`, `windspeed`, and `yr`.
- Basic residual diagnostics: residual-versus-fitted, Q--Q, and residual ACF.
- One chronological train/test split and test MAE, RMSE, and R-squared.
- Generated report tables, SBC article drafts in English and Brazilian
  Portuguese, and presentation outlines in both languages.
- Automated tests, linting, and one-command reproduction through `make all`.
- Equivalent didactic guides in English and Brazilian Portuguese.

## Decisions

- Use `weathersit` as recorded, with its four original levels.
- Use `log1p(cnt)` as the response scale.
- Use only `temp` among the temperature variables because `atemp` correlates
  0.988 with it.
- Keep `yr` categorical and train through September 2012 so both years are
  represented in the training data.
- Report test MAE, RMSE, and R-squared on the count scale after Duan's smearing
  back-transformation.

## Required before final submission

- Insert both authors' names, affiliations, and email addresses.
- Compile and visually inspect both `paper/main.tex` and `paper/main-pt-br.tex`
  in an SBC-compatible LaTeX environment.
- Confirm that both papers remain within 6--12 pages.
- Have both authors independently reproduce `make all` from a clean clone.
- Create the final slides, proofread the English, and tag the submitted release.
