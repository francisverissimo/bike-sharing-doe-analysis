# Bike Sharing DOE Analysis

Reproducible statistical analysis and demand prediction for the UCI Bike Sharing
Dataset. The analysis uses the 17,379 observed hours of 2011–2012 from the
Capital Bikeshare system in Washington, D.C.

The primary goals are to:

1. characterize the observational, naturally factorial design;
2. estimate main effects and interactions affecting hourly demand;
3. assess statistical assumptions and temporal dependence; and
4. build and chronologically validate a regression predictor for total rentals
   (`cnt`).

## Reproduce the analysis, step by step

The dataset is already included in the repository (`dataset/hour.csv`), so there
is nothing to download beyond the code. Run the commands below in a terminal, in
this order, from the project root after step 2.

### 1. Check the prerequisites

You need Git, GNU Make, and Python 3.10–3.12 with `venv` support (Python 3.10 is
the reference runtime):

```bash
python3 --version
make --version
git --version
```

On Debian/Ubuntu, install `venv` support first if it is missing, for example
`sudo apt install python3.10-venv`.

### 2. Get the code

```bash
git clone https://github.com/francisverissimo/bike-sharing-doe-analysis.git
cd bike-sharing-doe-analysis
```

If you already have a copy of the repository, just `cd` into it and run
`git pull` to make sure it is up to date.

### 3. Create the environment and install dependencies

```bash
make setup
```

This creates `.venv/` and installs the pinned dependencies listed in
`requirements.txt`. All `make` commands below use that environment
automatically; you do not need to activate it.

### 4. Check the installation

```bash
make lint
make test
```

`make lint` checks the Python code and `make test` runs the 8 automated tests.
Both must finish without errors before continuing.

### 5. Regenerate all results

```bash
make all
```

This runs the numbered scripts in `analysis/` in order: data validation,
descriptive analysis, DOE/ANOVA, assumptions and transformations, regression
models, temporal validation, and report summaries. Every table, figure and
diagnostic under `outputs/` is regenerated.

Individual stages are also available: `make validate`, `make eda`, `make doe`,
`make assumptions`, `make models`, `make prediction`, and `make report-assets`.

### 6. Read and verify the results

- `outputs/results_summary.md` (or `outputs/resumo_resultados.md` in Portuguese)
  is the readable summary of the final results.
- `outputs/tables/` contains the machine-readable tables.
- `outputs/figures/` and `outputs/diagnostics/` contain the plots.

In a clean checkout, regeneration must not change any tracked file:

```bash
git diff --exit-code
```

No output means the committed artifacts match a fresh reproduction. If you want
to run a script directly instead of through `make`, activate the environment
first with `source .venv/bin/activate`.

## Method

- One-way and type-II factorial ANOVA on `log1p(cnt)`, with effect sizes.
- Three prespecified hour interactions; BIC retains only `hr × workingday`.
- Progressive M0–M3 sequence on 2011 training data; the BIC winner is M4.
- Four response scales (`cnt`, `sqrt(cnt)`, `log1p(cnt)`, Box–Cox) evaluated.
- Full residual diagnostics, including ACF/PACF, leverage and Cook's distance.
- Strict 2011-to-2012 validation; `yr` is descriptive only.

The response is `cnt`; `casual` and `registered` are excluded as predictors.
Weather levels 3 and 4 are pooled because level 4 has only three hours.

Final results: M4 = M1 with 56 parameters, adjusted R-squared 0.920 and BIC
8673.5. Test MAE 87.67, RMSE 125.19, and R-squared 0.641. The Box–Cox exponent
is 0.315. These are associations and predictions from observational data, not
causal effects.

The protocol is in [`docs/analysis_protocol.md`](docs/analysis_protocol.md) and
the methodological decisions in [`docs/decision_log.md`](docs/decision_log.md).

## Dataset

`dataset/hour.csv` is the analysis dataset. `dataset/day.csv` is retained as part
of the original distribution. See `dataset/README.md` for provenance, citation,
license and checksums.

## Repository structure

```text
analysis/         Numbered, executable analysis scripts
dataset/          Original UCI data and documentation
docs/             Analysis protocol and methodological decisions
outputs/          Reproducible figures, tables, and diagnostics
src/bike_sharing/ Reusable Python code
tests/            Automated tests
```

## Authors

Adekola Alex Ajayi · Francis de Souza Veríssimo Ferreira
FACOM --- Universidade Federal do Mato Grosso do Sul (UFMS)
adekola.alex@ufms.br · francis.verissimo@ufms.br

## Citation

- Fanaee-T, H. and Gama, J. (2013). Event labeling combining ensemble detectors
  and background knowledge. *Progress in Artificial Intelligence*.
  <https://doi.org/10.1007/s13748-013-0040-3>
- UCI Machine Learning Repository. *Bike Sharing Dataset*.
  <https://doi.org/10.24432/C5W894>

## Licensing

The dataset is distributed by UCI under CC BY 4.0. No license has been granted
for the original code and text in this repository.
