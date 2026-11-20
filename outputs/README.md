# Generated outputs

Reproducible analysis artifacts are organized as follows:

- `figures/`: response distributions, factor boxplots, daily time series,
  correlations, main effects, the `workingday × hr` interaction, and test
  predictions;
- `tables/`: machine-readable summaries (including pooled weather means), ANOVA,
  Tukey HSD contrasts, response-scale comparison, test metrics, and LaTeX tables
  used by the papers;
- `diagnostics/`: residual plots and the residual autocorrelation function.

Figures and tables used in the papers are versioned with the script that produced
them. Temporary artifacts belong in `outputs/tmp/` and are ignored by Git.
