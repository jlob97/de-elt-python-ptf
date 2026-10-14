import argparse
import logging
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path

from amazon_elt.config import SpApiConfig
from amazon_elt.spapi.client import SpApiClient
from amazon_elt.spapi.reports import fetch_report, parse_flat_file
from amazon_elt.storage import write_parquet

logger = logging.getLogger(__name__)

REPORT_TYPE = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL"
RAW_DIR = Path("data/raw/order_items")
LOOKBACK_DAYS = 3


def extract_day(client: SpApiClient, marketplace_ids: list[str], day: date) -> None:
    start = datetime.combine(day, time(0), tzinfo=UTC)
    end = start + timedelta(days=1)

    data = fetch_report(client, REPORT_TYPE, marketplace_ids, start, end)
    rows = parse_flat_file(data)

    path = RAW_DIR / f"dt={day.isoformat()}" / "order_items.parquet"
    write_parquet(rows, path)
    logger.info("Wrote %d rows to %s", len(rows), path)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)

    yesterday = datetime.now(UTC).date() - timedelta(days=1)

    parser = argparse.ArgumentParser(description="Extract Amazon order items, one file per day")
    parser.add_argument(
        "--start",
        type=date.fromisoformat,
        default=yesterday - timedelta(days=LOOKBACK_DAYS - 1),
    )
    parser.add_argument("--end", type=date.fromisoformat, default=yesterday)
    args = parser.parse_args()

    if args.end > yesterday:
        parser.error("--end must be yesterday or earlier (today is not finished yet)")

    config = SpApiConfig.from_env()
    client = SpApiClient(config)

    day = args.start
    while day <= args.end:
        extract_day(client, config.marketplace_ids, day)
        day += timedelta(days=1)

    client.close()


if __name__ == "__main__":
    main()