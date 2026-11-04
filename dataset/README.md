# Dataset provenance

## Source

UCI Machine Learning Repository, **Bike Sharing Dataset**:

- DOI: <https://doi.org/10.24432/C5W894>
- Dataset page: <https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset>
- Creator: Hadi Fanaee-T
- Collection: Capital Bikeshare, Washington, D.C., 2011–2012

The original distribution contains hourly and daily aggregations. This project
uses `hour.csv` as its primary dataset because the hour-of-day factor is central
to the planned interaction analysis.

## Files

- `hour.csv`: 17,379 hourly observations; primary analysis data.
- `day.csv`: 731 daily observations; retained for provenance, not primary data.
- `Readme.txt`: original data dictionary and citation instructions.

The original CSV files must not be modified. Any derived data should be created
by code and stored separately only when necessary.

## Integrity checksums (SHA-256)

```text
e03de4ee4ef4dc376ac6e04bf829673c6269e8eba5c60fa121640fa2f829504f  hour.csv
a6bcf826782d3c0fbfdcbeead17cd0884185a0dafe8ff10cd48a874ee7ba18be  day.csv
b92c8628622948bf0828c43a1b315d1517c3d7fd63654730d0dea379b8e88175  Readme.txt
```

## License and required citation

UCI distributes the dataset under the **Creative Commons Attribution 4.0
International (CC BY 4.0)** license. Attribution must be retained.

Fanaee-T, H. and Gama, J. (2013). Event labeling combining ensemble detectors
and background knowledge. *Progress in Artificial Intelligence*, Springer.
<https://doi.org/10.1007/s13748-013-0040-3>
