"""Loading, enrichment, and validation for the hourly bike-sharing data."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from bike_sharing.config import (
    EXPECTED_COLUMNS,
    HOURLY_DATA,
    SEASON_LABELS,
    WEATHER_LABELS,
    WEEKDAY_LABELS,
    WORKING_DAY_LABELS,
    YEAR_LABELS,
)

EXPECTED_HOURLY_SHA256 = "e03de4ee4ef4dc376ac6e04bf829673c6269e8eba5c60fa121640fa2f829504f"


@dataclass(frozen=True)
class AuditCheck:
    """One machine-readable data-quality check."""

    check: str
    passed: bool
    observed: str
    expected: str


def sha256(path: Path) -> str:
    """Calculate a file's SHA-256 digest without loading it entirely in memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_hourly_data(path: Path = HOURLY_DATA) -> pd.DataFrame:
    """Load the original hourly CSV and add analysis-only derived columns."""
    data = pd.read_csv(path)
    data["dteday"] = pd.to_datetime(data["dteday"], format="%Y-%m-%d")
    data["timestamp"] = data["dteday"] + pd.to_timedelta(data["hr"], unit="h")

    data["season_label"] = pd.Categorical(
        data["season"].map(SEASON_LABELS),
        categories=list(SEASON_LABELS.values()),
        ordered=True,
    )
    data["weather_label"] = pd.Categorical(
        data["weathersit"].map(WEATHER_LABELS),
        categories=list(WEATHER_LABELS.values()),
        ordered=True,
    )
    data["workingday_label"] = pd.Categorical(
        data["workingday"].map(WORKING_DAY_LABELS),
        categories=list(WORKING_DAY_LABELS.values()),
    )
    data["year_label"] = pd.Categorical(
        data["yr"].map(YEAR_LABELS), categories=list(YEAR_LABELS.values()), ordered=True
    )
    data["weekday_label"] = pd.Categorical(
        data["weekday"].map(WEEKDAY_LABELS), categories=list(WEEKDAY_LABELS.values())
    )
    data["log1p_cnt"] = np.log1p(data["cnt"])
    return data


def find_missing_hours(data: pd.DataFrame) -> pd.DatetimeIndex:
    """Return timestamps absent between the first and final observed hour."""
    full_range = pd.date_range(data["timestamp"].min(), data["timestamp"].max(), freq="h")
    return full_range.difference(pd.DatetimeIndex(data["timestamp"]))


def audit_hourly_data(data: pd.DataFrame, path: Path = HOURLY_DATA) -> pd.DataFrame:
    """Run deterministic integrity checks against the original UCI distribution."""
    raw_columns = [column for column in data.columns if column in EXPECTED_COLUMNS]
    digest = sha256(path)
    missing_count = int(data[EXPECTED_COLUMNS].isna().sum().sum())
    count_violations = int((data["cnt"] != data["casual"] + data["registered"]).sum())
    binary_columns = ("yr", "holiday", "workingday")
    binary_valid = all(set(data[column]).issubset({0, 1}) for column in binary_columns)
    weather_columns = ["temp", "atemp", "hum", "windspeed"]
    normalized_valid = bool(
        data[weather_columns].apply(lambda column: column.between(0, 1).all()).all()
    )
    chronological = data["timestamp"].is_monotonic_increasing
    date_range_valid = data["dteday"].min() == pd.Timestamp("2011-01-01") and data[
        "dteday"
    ].max() == pd.Timestamp("2012-12-31")
    checks = [
        AuditCheck("sha256", digest == EXPECTED_HOURLY_SHA256, digest, EXPECTED_HOURLY_SHA256),
        AuditCheck("row_count", len(data) == 17_379, str(len(data)), "17379"),
        AuditCheck(
            "raw_columns",
            raw_columns == EXPECTED_COLUMNS,
            ",".join(raw_columns),
            ",".join(EXPECTED_COLUMNS),
        ),
        AuditCheck("missing_values", missing_count == 0, str(missing_count), "0"),
        AuditCheck(
            "unique_instant", data["instant"].is_unique, str(data["instant"].nunique()), "17379"
        ),
        AuditCheck(
            "unique_timestamp",
            data["timestamp"].is_unique,
            str(data["timestamp"].nunique()),
            "17379",
        ),
        AuditCheck(
            "count_identity", count_violations == 0, str(count_violations), "0 violations"
        ),
        AuditCheck(
            "positive_count",
            bool((data["cnt"] >= 1).all()),
            f"min={data['cnt'].min()}",
            "min>=1",
        ),
        AuditCheck(
            "hour_range",
            bool(data["hr"].between(0, 23).all()),
            f"{data['hr'].min()}..{data['hr'].max()}",
            "0..23",
        ),
        AuditCheck(
            "season_levels",
            set(data["season"]) == {1, 2, 3, 4},
            str(sorted(data["season"].unique())),
            "[1, 2, 3, 4]",
        ),
        AuditCheck(
            "weather_levels",
            set(data["weathersit"]) == {1, 2, 3, 4},
            str(sorted(data["weathersit"].unique())),
            "[1, 2, 3, 4]",
        ),
        AuditCheck(
            "binary_fields",
            binary_valid,
            "valid" if binary_valid else "invalid",
            "all values in {0,1}",
        ),
        AuditCheck(
            "normalized_weather",
            normalized_valid,
            "within range" if normalized_valid else "outside range",
            "all values in [0,1]",
        ),
        AuditCheck(
            "chronological_order",
            chronological,
            "monotonic" if chronological else "not monotonic",
            "monotonic",
        ),
        AuditCheck(
            "date_range",
            date_range_valid,
            f"{data['dteday'].min().date()}..{data['dteday'].max().date()}",
            "2011-01-01..2012-12-31",
        ),
    ]
    return pd.DataFrame(asdict(check) for check in checks)
