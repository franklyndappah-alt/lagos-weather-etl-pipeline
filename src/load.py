# These are the same pieces you ran in the notebook, turned into functions:

# create_tables makes the two tables you built by hand, and does nothing if they already exist.
# load_staging saves the raw copy. It uses "append" instead of "replace", 
# because the hash check already stops the same file loading twice, 
# and a real pipeline should keep adding new files.
# upsert_weather does the insert-or-update into weather_daily and returns how many rows it loaded



import pandas as pd
from sqlalchemy import text

CREATE_WEATHER_DAILY = """
CREATE TABLE IF NOT EXISTS weather_daily (
    city TEXT NOT NULL,
    date TEXT NOT NULL,
    temp_max_c REAL,
    temp_min_c REAL,
    precip_mm REAL,
    PRIMARY KEY (city, date)
);
"""

CREATE_RUN_LOG = """
CREATE TABLE IF NOT EXISTS etl_run_log (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT NOT NULL,
    file_hash TEXT,
    rows_read INTEGER,
    rows_loaded INTEGER,
    status TEXT NOT NULL,
    error_message TEXT,
    run_at TEXT NOT NULL
);
"""

UPSERT_SQL = """
INSERT INTO weather_daily (city, date, temp_max_c, temp_min_c, precip_mm)
VALUES (:city, :date, :temp_max_c, :temp_min_c, :precip_mm)
ON CONFLICT (city, date) DO UPDATE SET
    temp_max_c = excluded.temp_max_c,
    temp_min_c = excluded.temp_min_c,
    precip_mm  = excluded.precip_mm;
"""

def create_tables(engine):
    """Create the clean table and the run log if they don't exist yet."""
    with engine.begin() as conn:
        conn.execute(text(CREATE_WEATHER_DAILY))
        conn.execute(text(CREATE_RUN_LOG))

def load_staging(raw_df, engine, source_file):
    """Save an untouched copy of the raw rows into stg_weather."""
    stg = raw_df.copy()
    stg["source_file"] = source_file
    stg["loaded_at"] = pd.Timestamp.now().isoformat()
    stg.to_sql("stg_weather", engine, if_exists="append", index=False)
    return len(stg)

def upsert_weather(clean_df, engine):
    """Insert cleaned rows into weather_daily, updating any that already exist."""
    load = clean_df.copy()
    load["date"] = load["date"].dt.strftime("%Y-%m-%d")
    records = load.to_dict(orient="records")
    with engine.begin() as conn:
        conn.execute(text(UPSERT_SQL), records)
    return len(records)

def log_run(engine, file_name, file_hash, rows_read, rows_loaded, status, error_message=None):
    """Record one run of one file in etl_run_log."""
    row = {
        "file_name": file_name,
        "file_hash": file_hash,
        "rows_read": rows_read,
        "rows_loaded": rows_loaded,
        "status": status,
        "error_message": error_message,
        "run_at": pd.Timestamp.now().isoformat(),
    }
    sql = """
    INSERT INTO etl_run_log
        (file_name, file_hash, rows_read, rows_loaded, status, error_message, run_at)
    VALUES
        (:file_name, :file_hash, :rows_read, :rows_loaded, :status, :error_message, :run_at);
    """
    with engine.begin() as conn:
        conn.execute(text(sql), row)
# This is the insert you ran by hand earlier, wrapped in a function. 
# Instead of building the row in the notebook, 
# the pipeline will call log_run(...) once at the end of each run, 
# with status set to "success" or "rejected". 
# The error_message=None part means you can leave that argument out for successful runs.