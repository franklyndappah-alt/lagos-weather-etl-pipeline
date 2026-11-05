# This is for the automated download of the Lagos weather CSV from Open-Meteo.

import requests
from datetime import date, timedelta
from pathlib import Path

def download_lagos_csv(inbox="data/inbox", days_back=30, lag_days=5):
    """Download the most recent weather window for Lagos into the inbox."""
    end = date.today() - timedelta(days=lag_days)
    start = end - timedelta(days=days_back)
    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        "?latitude=6.5244&longitude=3.3792"
        f"&start_date={start}&end_date={end}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        "&timezone=Africa%2FLagos&format=csv"
    )
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()

    Path(inbox).mkdir(parents=True, exist_ok=True)
    out = Path(inbox) / f"Lagos_weather_{end}.csv"
    out.write_bytes(resp.content)
    return out