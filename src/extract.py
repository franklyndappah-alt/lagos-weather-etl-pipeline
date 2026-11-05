# This is my extraction code from the notebook, wrapped in a function. 
# The function takes a file path, so it can read any CSV instead of only Lagos_weather.csv.
import hashlib
from pathlib import Path
import pandas as pd

def read_weather_csv(path):
    """Read one Open-Meteo CSV, skipping the metadata block."""
    return pd.read_csv(path, skiprows=3)

def file_hash(path):
    """Fingerprint of a file's contents, used to spot files already processed."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def get_processed_hashes(engine):
    """Return the set of hashes for files that were already loaded successfully."""
    df = pd.read_sql("SELECT file_hash FROM etl_run_log WHERE status = 'success'", engine)
    return set(df["file_hash"])
# get_processed_hashes reads the fingerprints of successful runs from etl_run_log into a set, 
# which is a fast lookup list.

def is_new_file(path, processed_hashes):
    """True if this file's hash is not in the log yet."""
    return file_hash(path) not in processed_hashes
# is_new_file returns True for a new file and False for one the pipeline has seen.

def find_new_files(inbox, processed_hashes):
    """Return the CSVs in the inbox folder that have not been processed yet."""
    inbox = Path(inbox)
    return [
        path for path in sorted(inbox.glob("*.csv")) #inbox.glob("*.csv") lists every CSV in the folder.
        if is_new_file(path, processed_hashes)  
    ]
# The inbox is a folder where new CSVs are dropped. find_new_files returns a list of the new files, 
# sorted by name, that have not been processed yet.