# This is the same function I wrote in the notebook. 
# The one change is that expected_columns is now a constant named EXPECTED_COLUMNS inside the file, 
# so the function no longer depends on a notebook variable. 
# That matters because a scheduled script has no notebook memory to borrow from.


import pandas as pd

EXPECTED_COLUMNS = [
    "time",
    "temperature_2m_max (°C)",
    "temperature_2m_min (°C)",
    "precipitation_sum (mm)",
]

def validate_weather(df):
    """Run all quality checks. Returns a dict of check name -> True/False."""
    dates = pd.to_datetime(df["time"], errors="coerce")

    checks = {
        "schema": list(df.columns) == EXPECTED_COLUMNS,
        "row_count": len(df) > 0,
        "no_nulls": not df.isnull().any().any(),
        "valid_dates": dates.notnull().all(),
        "unique_dates": df["time"].is_unique,
        "no_missing_days": len(pd.date_range(dates.min(), dates.max(), freq="D")) == len(df),
        "temp_max_range": df["temperature_2m_max (°C)"].between(15, 45).all(),
        "temp_min_range": df["temperature_2m_min (°C)"].between(15, 45).all(),
        "rain_range": (df["precipitation_sum (mm)"] >= 0).all(),
        "max_gte_min": (df["temperature_2m_max (°C)"] >= df["temperature_2m_min (°C)"]).all(),
        "no_future_dates": dates.max() <= pd.Timestamp.today(),
    }
    return {name: bool(result) for name, result in checks.items()}