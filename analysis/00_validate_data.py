"""Audit the untouched UCI hourly dataset and write reproducible audit artifacts."""

from __future__ import annotations

import json

import pandas as pd

from bike_sharing.config import TABLES_DIR, ensure_output_directories
from bike_sharing.data import audit_hourly_data, find_missing_hours, load_hourly_data


def main() -> None:
    ensure_output_directories()
    data = load_hourly_data()
    audit = audit_hourly_data(data)
    missing_hours = find_missing_hours(data)

    audit.to_csv(TABLES_DIR / "data_audit.csv", index=False)
    missing_hours.to_frame(index=False, name="missing_timestamp").to_csv(
        TABLES_DIR / "missing_hours.csv", index=False
    )

    factor_counts = []
    for factor in ("season", "yr", "hr", "holiday", "weekday", "workingday", "weathersit"):
        counts = data[factor].value_counts().sort_index()
        factor_counts.extend(
            {"factor": factor, "level": str(level), "n": int(count)}
            for level, count in counts.items()
        )
    factor_counts_frame = pd.DataFrame(factor_counts)
    factor_counts_frame.to_csv(TABLES_DIR / "factor_counts.csv", index=False)

    summary = {
        "rows": len(data),
        "calendar_days": int(data["dteday"].nunique()),
        "first_timestamp": data["timestamp"].min().isoformat(),
        "last_timestamp": data["timestamp"].max().isoformat(),
        "missing_hourly_timestamps": len(missing_hours),
        "weather_level_4_rows": int((data["weathersit"] == 4).sum()),
        "all_checks_passed": bool(audit["passed"].all()),
    }
    (TABLES_DIR / "data_audit_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    print(json.dumps(summary, indent=2))
    if not summary["all_checks_passed"]:
        failed = audit.loc[~audit["passed"]]
        raise SystemExit(f"Data audit failed:\n{failed.to_string(index=False)}")


if __name__ == "__main__":
    main()
