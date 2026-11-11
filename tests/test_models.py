import numpy as np

from bike_sharing.models import prediction_metrics


def test_prediction_metrics_are_zero_for_perfect_predictions() -> None:
    observed = np.array([1.0, 10.0, 100.0])
    metrics = prediction_metrics(observed, observed.copy())
    assert metrics["mae"] == 0
    assert metrics["rmse"] == 0
    assert metrics["r2"] == 1
    assert metrics["rmsle"] == 0
