# Now we are moving to test the Validate_weather to know if our validations works well.
# What it does is that, it checks a file to see if it's good or bad and allows the good one and stops the bad one.


import pandas as pd
from src.validate import validate_weather


def make_good():
    return pd.DataFrame({
        "time": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "temperature_2m_max (°C)": [33.0, 32.0, 31.0],
        "temperature_2m_min (°C)": [22.0, 21.0, 23.0],
        "precipitation_sum (mm)": [0.0, 1.2, 0.0],
    })


def test_good_data_passes_every_check():
    results = validate_weather(make_good())
    assert all(results.values())


def test_null_value_fails_no_nulls():
    df = make_good()
    df.loc[1, "precipitation_sum (mm)"] = None
    assert validate_weather(df)["no_nulls"] is False


def test_missing_day_fails_no_missing_days():
    df = make_good().drop(index=1)
    assert validate_weather(df)["no_missing_days"] is False


def test_duplicate_date_fails_unique_dates():
    df = pd.concat([make_good(), make_good().iloc[[0]]], ignore_index=True)
    assert validate_weather(df)["unique_dates"] is False


def test_impossible_temperature_fails_range():
    df = make_good()
    df.loc[0, "temperature_2m_max (°C)"] = 99.0
    assert validate_weather(df)["temp_max_range"] is False


def test_max_below_min_fails_consistency():
    df = make_good()
    df.loc[0, "temperature_2m_max (°C)"] = 20.0
    df.loc[0, "temperature_2m_min (°C)"] = 25.0
    assert validate_weather(df)["max_gte_min"] is False


def test_future_date_fails_timeliness():
    df = make_good()
    df.loc[2, "time"] = "2099-01-03"
    assert validate_weather(df)["no_future_dates"] is False