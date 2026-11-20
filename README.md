# Bike Sharing DOE Analysis

[Português (Brasil)](README.pt-BR.md) | **English**

Statistical analysis and demand prediction for the UCI Bike Sharing Dataset,
developed for a Design of Experiments course assignment. The final narrative is
deliberately centered on one question: how working-day status changes the hourly
demand profile.

The project uses the hourly observations from the Capital Bikeshare system in
Washington, D.C. (2011–2012). Its primary goals are to:

1. characterize the observational, naturally factorial design of the data;
2. estimate and interpret main effects and interactions affecting hourly demand;
3. assess statistical assumptions and temporal dependence; and
4. build and chronologically validate a justified regression predictor for total
   bike rentals (`cnt`).

## Status

The simplified bilingual analysis is available on the
`feat/simplified-bilingual-analysis` branch. The statistical protocol is documented in
[`docs/analysis_protocol.md`](docs/analysis_protocol.md), and consequential
methodological decisions are recorded in
[`docs/decision_log.md`](docs/decision_log.md).

Read the complete didactic walkthrough in either language:

- [Português (Brasil)](docs/tutorial-pt-br.md)
- [English](docs/tutorial-en.md)

The SBC article is also maintained in both languages:

- [English article](paper/main.tex) — canonical submission source
- [Brazilian Portuguese article](paper/main-pt-br.tex) — study and review version

## Dataset

The analysis uses `dataset/hour.csv`, which contains 17,379 hourly observations.
`dataset/day.csv` is retained as part of the original distribution but is not the
primary analysis dataset.

The response is `cnt`, the sum of casual and registered rentals. `casual` and
`registered` will not be predictors because doing so would leak the response's
components into the model.

See [`dataset/README.md`](dataset/README.md) for provenance, citation, license,
and file checksums.

## Repository structure

```text
analysis/              Numbered, executable analysis scripts
dataset/               Original UCI data and documentation
deliverables/proposal/ Submitted proposal and its SBC source
docs/                   Protocol, decisions, plans, and source screenshots
outputs/                Reproducible figures, tables, and diagnostics
paper/                  SBC paper source and selected figures
presentation/           Presentation source and assets
src/bike_sharing/       Reusable Python code
tests/                  Automated tests
```

## Python environment

Python 3.10 is the reference runtime.

```bash
make setup
make test
make lint
```

Activate the environment manually when needed:

```bash
source .venv/bin/activate
```

Run the complete MVP pipeline with:

```bash
make all
```

This command audits the data and reproduces every table and figure used by the
paper draft. The active comparison contains only additive M0 and interaction M1.
Individual stages are available as `make validate`, `make eda`,
`make doe`, `make assumptions`, `make models`, `make prediction`, and
`make report-assets`.

## Collaboration

The two authors work directly on `main`. Every commit must be complete, focused,
and reproducible. See [`CONTRIBUTING.md`](CONTRIBUTING.md) before making changes.

## Citation

If this repository or dataset is used, cite the original publication and UCI
dataset:

- Fanaee-T, H. and Gama, J. (2013). Event labeling combining ensemble detectors
  and background knowledge. *Progress in Artificial Intelligence*.
  <https://doi.org/10.1007/s13748-013-0040-3>
- UCI Machine Learning Repository. *Bike Sharing Dataset*.
  <https://doi.org/10.24432/C5W894>

## Licensing

The dataset is distributed by UCI under the Creative Commons Attribution 4.0
International license (CC BY 4.0). No license has yet been granted for the code
or original written material in this repository.
