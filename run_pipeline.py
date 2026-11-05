# Now we connect all the pieces into one script that runs them in the order of our DAG.




import logging
from pathlib import Path

from sqlalchemy import create_engine

from src.extract import file_hash, read_weather_csv, get_processed_hashes, find_new_files
from src.validate import validate_weather
from src.transform import transform_weather
from src.load import create_tables, load_staging, upsert_weather, log_run
from src.files import move_file
from src.download import download_lagos_csv

DB_URL = "sqlite:///lag_weather.db"
INBOX = "data/inbox"

Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.FileHandler("logs/pipeline.log"), logging.StreamHandler()],
)
log = logging.getLogger("pipeline")


def process_file(path, engine):
    """Run one CSV through staging, validation, transform, load, log and move."""
    path = Path(path)
    city = path.stem.split("_")[0].title()   # Lagos_weather.csv -> Lagos
    h = file_hash(path)
    rows_read = 0

    try:
        raw_df = read_weather_csv(path)
        rows_read = len(raw_df)
        log.info("Extracted %s (%d rows)", path.name, rows_read)

        load_staging(raw_df, engine, path.name)
        log.info("Saved raw rows to stg_weather")

        results = validate_weather(raw_df)
        failed = [name for name, ok in results.items() if not ok]
        if failed:
            message = "Failed checks: " + ", ".join(failed)
            log.warning("%s rejected. %s", path.name, message)
            log_run(engine, path.name, h, rows_read, 0, "rejected", message)
            move_file(path, "rejected")
            return

        clean_df = transform_weather(raw_df, city)
        rows_loaded = upsert_weather(clean_df, engine)
        log.info("Loaded %d rows into weather_daily", rows_loaded)

        log_run(engine, path.name, h, rows_read, rows_loaded, "success")
        move_file(path, "success")
        log.info("%s finished successfully", path.name)

    except Exception as error:
        log.exception("%s crashed", path.name)
        log_run(engine, path.name, h, rows_read, 0, "rejected", str(error))
        move_file(path, "rejected")


def main():
    engine = create_engine(DB_URL)
    create_tables(engine)
    
    try:
        downloaded = download_lagos_csv(INBOX)
        log.info("Downloaded %s", downloaded.name)
    except Exception:
        log.exception("Download failed, continuing with files already in the inbox")

    processed_hashes = get_processed_hashes(engine)
    new_files = find_new_files(INBOX, processed_hashes)

    if not new_files:
        log.info("No new files in the inbox. Nothing to do.")
        return

    log.info("Found %d new file(s)", len(new_files))
    for path in new_files:
        process_file(path, engine)
    log.info("Run finished")


if __name__ == "__main__":
    main()