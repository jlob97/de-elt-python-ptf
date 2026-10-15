from pathlib import Path

from amazon_elt.extract.runner import run_report_snapshot

REPORT_TYPE = "GET_MERCHANT_LISTINGS_ALL_DATA"
RAW_DIR = Path("data/raw/listings")

if __name__ == "__main__":
    run_report_snapshot(REPORT_TYPE, RAW_DIR)
