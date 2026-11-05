import pandas as pd
from src.transform import transform_weather


def make_raw():
    return pd.DataFrame({
        "time": ["2024-01-01", "2024-01-02", "2024-01-02"],
        "temperature_2m_max (°C)": [33.0, 32.5, 32.5],
        "temperature_2m_min (°C)": [22.0, 21.5, 21.5],
        "precipitation_sum (mm)": [0.0, 1.2, 1.2],
    })


def test_columns_are_renamed_and_ordered():
    result = transform_weather(make_raw(), "Lagos")
    assert list(result.columns) == ["city", "date", "temp_max_c", "temp_min_c", "precip_mm"]


def test_city_is_added():
    result = transform_weather(make_raw(), "Lagos")
    assert (result["city"] == "Lagos").all()


def test_date_becomes_a_real_date():
    result = transform_weather(make_raw(), "Lagos")
    assert str(result["date"].dtype).startswith("datetime64")


def test_duplicate_days_are_removed():
    result = transform_weather(make_raw(), "Lagos")
    assert len(result) == 2