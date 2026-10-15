from pathlib import Path

from amazon_elt.extract.runner import run_report_stream

REPORT_TYPE = "GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA"
RAW_DIR = Path("data/raw/fba_returns")
DROP_COLUMNS = ("customer-comments",)

if __name__ == "__main__":
    run_report_stream(REPORT_TYPE, RAW_DIR, DROP_COLUMNS)