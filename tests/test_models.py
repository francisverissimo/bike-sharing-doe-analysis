import numpy as np

from bike_sharing.models import EXPLANATORY_FORMULAS, PREDICTIVE_FORMULAS, prediction_metrics


def test_prediction_metrics_are_zero_for_perfect_predictions() -> None:
    observed = np.array([1.0, 10.0, 100.0])
    metrics = prediction_metrics(observed, observed.copy())
    assert metrics["mae"] == 0
    assert metrics["rmse"] == 0
    assert metrics["r2"] == 1
    assert metrics["rmsle"] == 0


def test_simplified_scope_contains_only_additive_and_primary_interaction_models() -> None:
    assert list(EXPLANATORY_FORMULAS) == ["M0_main_effects", "M1_workingday_hour"]
    assert list(PREDICTIVE_FORMULAS) == ["P0_main_effects", "P1_workingday_hour"]
    assert "C(hr) * C(workingday)" in EXPLANATORY_FORMULAS["M1_workingday_hour"]
