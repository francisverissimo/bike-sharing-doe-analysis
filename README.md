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

The response is `cnt`; `casual` and `registered` are excluded as predictors.
Weather levels 3 and 4 are pooled because level 4 has only three hours.

## Method

- One-way and type-II factorial ANOVA on `log1p(cnt)`, with effect sizes.
- Three prespecified hour interactions; BIC retains only `hr × workingday`.
- Progressive M0–M3 sequence on 2011 training data; the BIC winner is M4.
- Four response scales (`cnt`, `sqrt(cnt)`, `log1p(cnt)`, Box–Cox) evaluated.
- Full residual diagnostics, including ACF/PACF, leverage and Cook's distance.
- Strict 2011-to-2012 validation; `yr` is descriptive only.

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

## Python environment

Python 3.10 is the reference runtime.

```bash
make setup
make test
make lint
```

Activate the environment manually with `source .venv/bin/activate` when needed.

## Running the analysis

```bash
make all
```

This audits the data and regenerates every table, figure and diagnostic under
`outputs/`. Individual stages are available as `make validate`, `make eda`,
`make doe`, `make assumptions`, `make models`, `make prediction`, and
`make report-assets`.

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
