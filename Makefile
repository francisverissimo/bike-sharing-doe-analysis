PYTHON := .venv/bin/python
PIP := .venv/bin/pip
RUFF := .venv/bin/ruff
PYTEST := .venv/bin/pytest

.PHONY: help setup lint test all

help:
	@echo "Available targets:"
	@echo "  setup  Create .venv and install pinned dependencies"
	@echo "  lint   Check Python source and tests with Ruff"
	@echo "  test   Run automated tests"
	@echo "  all    Reproduce the full analysis (added in later phases)"

setup:
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

lint:
	$(RUFF) check src tests analysis

test:
	$(PYTEST)

all:
	@echo "The complete analysis pipeline has not been implemented yet."
