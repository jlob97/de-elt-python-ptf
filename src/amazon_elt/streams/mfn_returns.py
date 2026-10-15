from pathlib import Path

from amazon_elt.extract.runner import run_report_stream

REPORT_TYPE = "GET_FLAT_FILE_RETURNS_DATA_BY_RETURN_DATE"
RAW_DIR = Path("data/raw/mfn_returns")
LOOKBACK_DAYS = 30

if __name__ == "__main__":
    run_report_stream(REPORT_TYPE, RAW_DIR, lookback_days=LOOKBACK_DAYS)