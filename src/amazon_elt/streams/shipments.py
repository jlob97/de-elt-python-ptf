from pathlib import Path

from amazon_elt.extract.runner import run_report_stream

REPORT_TYPE = "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL"
RAW_DIR = Path("data/raw/shipments")

if __name__ == "__main__":
    run_report_stream(REPORT_TYPE, RAW_DIR)
