import numpy as np

from bike_sharing.models import MODEL_FORMULA, model_formula, prediction_metrics


def test_prediction_metrics_are_zero_for_perfect_predictions() -> None:
    observed = np.array([1.0, 10.0, 100.0])
    metrics = prediction_metrics(observed, observed.copy())
    assert metrics["mae"] == 0
    assert metrics["rmse"] == 0
    assert metrics["r2"] == 1
    assert set(metrics) == {"mae", "rmse", "r2"}


def test_single_model_formula_matches_proposal_scope() -> None:
    formula = model_formula()
    assert formula == MODEL_FORMULA.format(target="log1p_cnt")
    for term in (
        "C(hr) * C(workingday)",
        "C(weathersit)",
        "C(season)",
        "temp",
        "hum",
        "windspeed",
        "C(yr)",
    ):
        assert term in formula
    assert "weather_group" not in formula
    assert "time_index_days" not in formula
