# Contributing

This is a two-person academic project. Both contributors work directly on
`main`, so coordination and small commits are required.

## Before editing

1. Open or select a GitHub issue for the task.
2. Tell the other contributor which files you intend to edit.
3. Run `git status` and ensure no unrelated work will be overwritten.
4. Synchronize with `git pull --rebase origin main` when a remote is configured.

Do not edit the same file concurrently without explicit coordination.

## Before pushing

```bash
make lint
make test
git status
git pull --rebase origin main
git push origin main
```

Never force-push `main`. Do not rewrite commits that have already been shared.

## Commit messages

Use an imperative Conventional Commit prefix:

```text
chore: configure reproducible Python environment
docs: define statistical analysis protocol
feat(data): validate hourly observations
analysis: add descriptive statistics and plots
analysis: evaluate main effects and interactions
feat(model): compare explanatory regression models
feat(validation): add chronological model evaluation
docs(paper): report regression diagnostics
```

Keep implementation, generated results, and unrelated formatting in separate
commits. Explain the statistical motivation in the commit body when it is not
obvious from the diff.

## Research decisions

Any decision that changes the interpretation or reproducibility of the study
must also be added to `docs/decision_log.md`. Examples include response
transformations, factor regrouping, interaction selection, temporal validation,
and treatment of influential observations.

Generated figures and tables used in the paper should be committed alongside
the script changes that generated them.
