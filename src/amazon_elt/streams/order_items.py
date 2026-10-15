from pathlib import Path

from amazon_elt.extract.runner import run_report_stream

REPORT_TYPE = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL"
RAW_DIR = Path("data/raw/order_items")

if __name__ == "__main__":
    run_report_stream(REPORT_TYPE, RAW_DIR)