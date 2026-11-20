# Presentation

The English slide deck is generated from the versioned analysis artifacts:

```bash
make slides
```

- `build_slides.py` creates `bike-sharing-analysis.pptx` deterministically from
  the tables and figures under `outputs/`.
- `bike-sharing-analysis.pptx` contains 17 slides with speaker notes: overview,
  data and design, descriptive results, factorial effects, ANOVA, Tukey HSD,
  response scale, residual diagnostics, the single model, temporal validation,
  predictions and limitations.
- `outline.md` is the English talking-point outline; `roteiro-pt-br.md` is the
  Brazilian Portuguese counterpart used when preparing the oral presentation.

The slide deck is included in `make all`, so the CI reproduction check also
verifies that the committed `.pptx` is current.
