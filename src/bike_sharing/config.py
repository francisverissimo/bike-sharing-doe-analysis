"""Project paths, labels, and plotting constants."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "dataset"
HOURLY_DATA = DATA_DIR / "hour.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUT_DIR / "figures"
TABLES_DIR = OUTPUT_DIR / "tables"
DIAGNOSTICS_DIR = OUTPUT_DIR / "diagnostics"

# The proposal specifies one calendar year for training and the next for testing.
TRAIN_START = "2011-01-01"
TRAIN_END = "2011-12-31 23:59:59"
TEST_START = "2012-01-01"
TEST_END = "2012-12-31 23:59:59"

# Response candidates evaluated before fixing the final modelling scale.
CANDIDATE_SCALES = ("cnt", "sqrt_cnt", "log1p_cnt", "boxcox_cnt")
FINAL_RESPONSE = "log1p_cnt"

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
