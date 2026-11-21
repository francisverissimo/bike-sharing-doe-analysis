# Analysis scripts

The numbered scripts reproduce the final analysis end to end. They validate the
hourly data, describe `cnt`, plot main effects and the three prespecified hour
interactions, report one-way and factorial ANOVA with Tukey contrasts, compare
the M0–M4 sequence and four response scales, run the full diagnostic checklist,
and evaluate strict 2011-to-2012 prediction with MAE, RMSE and R-squared.

1. `00_validate_data.py`
2. `01_descriptive_analysis.py`
3. `02_doe_analysis.py`
4. `03_assumptions_transformations.py`
5. `04_regression_models.py`
6. `05_temporal_validation.py`
7. `06_report_assets.py`

Reusable functions belong in `src/bike_sharing/`. Scripts orchestrate an
analysis, save deterministic artifacts under `outputs/`, and avoid duplicating
statistical or plotting logic. Run the full sequence with `make all`.
