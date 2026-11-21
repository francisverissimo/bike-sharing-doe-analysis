import numpy as np

from bike_sharing.models import (
    MODEL_FORMULA,
    MODEL_ORDER,
    MODEL_SEQUENCE,
    model_formula,
    prediction_metrics,
    select_model_by_bic,
)
from bike_sharing.transforms import backtransform


def test_prediction_metrics_are_zero_for_perfect_predictions() -> None:
    observed = np.array([1.0, 10.0, 100.0])
    metrics = prediction_metrics(observed, observed.copy())
    assert metrics["mae"] == 0
    assert metrics["rmse"] == 0
    assert metrics["r2"] == 1
    assert set(metrics) == {"mae", "rmse", "r2"}


def test_final_model_formula_matches_proposal_scope() -> None:
    formula = model_formula()
    assert formula == MODEL_FORMULA.format(target="log1p_cnt")
    for term in (
        "C(hr) * C(workingday)",
        "C(weather_group)",
        "C(season)",
        "temp",
        "hum",
        "windspeed",
    ):
        assert term in formula
    assert "C(yr)" not in formula
    assert "C(weathersit)" not in formula
    assert "time_index_days" not in formula


def test_model_sequence_is_nested_and_ordered() -> None:
    assert MODEL_ORDER == ("M0", "M1", "M2", "M3")
    assert "C(hr) * C(workingday)" in MODEL_SEQUENCE["M1"]
    assert "C(hr) * C(weather_group)" in MODEL_SEQUENCE["M2"]
    assert "C(hr) * C(season)" in MODEL_SEQUENCE["M2"]
    assert "I(temp**2)" in MODEL_SEQUENCE["M3"]


def test_bic_selection_prefers_first_model_when_tied() -> None:
    class FakeModel:
        def __init__(self, bic: float) -> None:
            self.bic = bic

    fits = {name: FakeModel(100.0) for name in MODEL_ORDER}
    assert select_model_by_bic(fits) == "M0"


def test_log_backtransform_uses_smearing_factor() -> None:
    predicted = backtransform("log1p_cnt", np.array([0.0, 1.0]), np.array([0.0, 0.0]))
    assert np.allclose(predicted, [0.0, np.e - 1])
