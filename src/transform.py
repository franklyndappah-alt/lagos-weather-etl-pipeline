# This is the same work I did in the notebook, wrapped in one function with two inputs:
# df is the raw data to clean.
# city is the city name. Before, "Lagos" was typed directly into the code. Now it’s passed in, 
# so the same function can clean a file for any city.
# The function starts with df.copy(), so it never changes the DataFrame you hand it, 
# and it behaves the same way every time you call it.



import pandas as pd

def transform_weather(df, city):
    """Clean a raw Open-Meteo DataFrame and return it ready for the database."""
    clean = df.copy()

    clean = clean.rename(columns={
        "time": "date",
        "temperature_2m_max (°C)": "temp_max_c",
        "temperature_2m_min (°C)": "temp_min_c",
        "precipitation_sum (mm)": "precip_mm",
    })

    clean["date"] = pd.to_datetime(clean["date"])
    clean["city"] = city

    clean = clean[["city", "date", "temp_max_c", "temp_min_c", "precip_mm"]]
    clean = clean.drop_duplicates(subset=["city", "date"])

    return clean