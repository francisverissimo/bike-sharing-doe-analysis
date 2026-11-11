# Analysis scripts

This directory will contain numbered, executable scripts:

1. `00_validate_data.py`
2. `01_descriptive_analysis.py`
3. `02_doe_analysis.py`
4. `03_assumptions_transformations.py`
5. `04_regression_models.py`
6. `05_temporal_validation.py`
7. `06_report_assets.py`

Reusable functions belong in `src/bike_sharing/`. Scripts should orchestrate an
analysis, save deterministic artifacts under `outputs/`, and avoid duplicating
statistical or plotting logic.
