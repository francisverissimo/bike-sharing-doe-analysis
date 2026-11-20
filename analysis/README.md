# Analysis scripts

The active scope is deliberately narrow: compare additive M0 with M1, which adds
only the prespecified `hour × working day` interaction. The predictive stage
compares a historical baseline, P0, and P1 using chronological windows.

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

For a concept-by-concept explanation, read `docs/tutorial-en.md` or
`docs/tutorial-pt-br.md`.
