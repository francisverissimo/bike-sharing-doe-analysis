# Analysis scripts

The analysis follows the proposal with one regression model. It describes `cnt`,
plots the main effects of `hr`, `workingday`, `weathersit`, and `season`, plots the
`workingday × hr` interaction, reports a factorial ANOVA, compares `cnt` with
`log1p(cnt)`, checks basic residual diagnostics, and evaluates one chronological
train/test split with MAE, RMSE, and R-squared.

The numbered scripts are:

1. `00_validate_data.py`
2. `01_descriptive_analysis.py`
3. `02_doe_analysis.py`
4. `03_assumptions_transformations.py`
5. `04_regression_models.py`
6. `05_temporal_validation.py`
7. `06_report_assets.py`

Reusable functions belong in `src/bike_sharing/`. Scripts orchestrate an
analysis, save deterministic artifacts under `outputs/`, and avoid duplicating
statistical or plotting logic.

For a concept-by-concept explanation, read `docs/tutorial-en.md` or
`docs/tutorial-pt-br.md`.
