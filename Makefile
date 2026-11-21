PYTHON := .venv/bin/python
PIP := .venv/bin/pip
RUFF := .venv/bin/ruff
PYTEST := .venv/bin/pytest

.PHONY: help setup lint test validate eda doe assumptions models prediction report-assets all

help:
	@echo "Available targets:"
	@echo "  setup  Create .venv and install pinned dependencies"
	@echo "  lint   Check Python source and tests with Ruff"
	@echo "  test   Run automated tests"
	@echo "  all    Reproduce every analysis artifact"

setup:
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

lint:
	$(RUFF) check src tests analysis

test:
	$(PYTEST)

validate:
	$(PYTHON) analysis/00_validate_data.py

eda: validate
	$(PYTHON) analysis/01_descriptive_analysis.py

doe: eda
	$(PYTHON) analysis/02_doe_analysis.py

assumptions: doe
	$(PYTHON) analysis/03_assumptions_transformations.py

models: assumptions
	$(PYTHON) analysis/04_regression_models.py

prediction: models
	$(PYTHON) analysis/05_temporal_validation.py

report-assets: prediction
	$(PYTHON) analysis/06_report_assets.py

all: report-assets
