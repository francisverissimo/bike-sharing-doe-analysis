# Paper

This directory contains the source of the final 6--12 page research article in
the Brazilian Computer Society (SBC) format.

`reference-template.tex`, `sbc-template.sty`, and `sbc.bst` originate from the
SBC template distribution. Generated PDFs should be copied to `deliverables/`
for a submission snapshot.

## Article versions

- `main.tex`: canonical English submission source.
- `main-pt-br.tex`: Brazilian Portuguese version for study, review, and
  presentation preparation.

Both versions share the same generated tables in `../outputs/tables/`, the same
figures in `../outputs/figures/`, and the same bibliography in
`references.bib`. Keep sections, labels, citations, numbers, and conclusions in
sync when either file changes. The English `abstract` is retained in the
Portuguese version, followed by the Portuguese `resumo`.

CI compiles both files with the SBC template and uploads both PDFs.
