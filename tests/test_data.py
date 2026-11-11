from bike_sharing.data import audit_hourly_data, find_missing_hours, load_hourly_data


def test_original_hourly_data_passes_audit() -> None:
    data = load_hourly_data()
    audit = audit_hourly_data(data)
    assert audit["passed"].all()


def test_derived_columns_and_weather_group_are_consistent() -> None:
    data = load_hourly_data()
    assert len(data) == 17_379
    assert data["timestamp"].is_unique
    assert (data["cnt"] == data["casual"] + data["registered"]).all()
    assert int((data["weather_group"] == "Precipitation/adverse").sum()) == 1_422
    assert len(find_missing_hours(data)) == 165
