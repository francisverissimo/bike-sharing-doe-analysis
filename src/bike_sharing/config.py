"""Project paths, labels, and plotting constants."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "dataset"
HOURLY_DATA = DATA_DIR / "hour.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUT_DIR / "figures"
TABLES_DIR = OUTPUT_DIR / "tables"
DIAGNOSTICS_DIR = OUTPUT_DIR / "diagnostics"

EXPECTED_COLUMNS = [
    "instant",
    "dteday",
    "season",
    "yr",
    "mnth",
    "hr",
    "holiday",
    "weekday",
    "workingday",
    "weathersit",
    "temp",
    "atemp",
    "hum",
    "windspeed",
    "casual",
    "registered",
    "cnt",
]

SEASON_LABELS = {
    1: "Spring",
    2: "Summer",
    3: "Fall",
    4: "Winter",
}
WEATHER_LABELS = {
    1: "Clear/partly cloudy",
    2: "Mist/cloudy",
    3: "Light precipitation",
    4: "Severe weather",
}
WEATHER_GROUP_LABELS = {
    1: "Clear/partly cloudy",
    2: "Mist/cloudy",
    3: "Precipitation/adverse",
}
WORKING_DAY_LABELS = {0: "Non-working day", 1: "Working day"}
YEAR_LABELS = {0: "2011", 1: "2012"}
WEEKDAY_LABELS = {
    0: "Sunday",
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday",
}


def ensure_output_directories() -> None:
    """Create every directory used by generated analysis artifacts."""
    for directory in (FIGURES_DIR, TABLES_DIR, DIAGNOSTICS_DIR):
        directory.mkdir(parents=True, exist_ok=True)
