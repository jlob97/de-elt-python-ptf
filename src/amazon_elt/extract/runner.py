import argparse
import logging
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path

from amazon_elt.config import SpApiConfig
from amazon_elt.extract.storage import write_parquet
from amazon_elt.spapi.client import SpApiClient
from amazon_elt.spapi.reports import fetch_report, parse_flat_file

logger = logging.getLogger(__name__)

LOOKBACK_DAYS = 3


def extract_report_day(
    client: SpApiClient,
    report_type: str,
    marketplace_ids: list[str],
    day: date,
    raw_dir: Path,
    drop_columns: tuple[str, ...] = (),
) -> None:
    start = datetime.combine(day, time(0), tzinfo=UTC)
    end = start + timedelta(days=1)

    data = fetch_report(client, report_type, marketplace_ids, start, end)
    rows = parse_flat_file(data)

    for row in rows:
        for column in drop_columns:
            row.pop(column, None)

    path = raw_dir / f"dt={day.isoformat()}" / f"{raw_dir.name}.parquet"
    write_parquet(rows, path)
    logger.info("Wrote %d rows to %s", len(rows), path)


def run_report_stream(
    report_type: str,
    raw_dir: Path,
    drop_columns: tuple[str, ...] = (),
    lookback_days: int = LOOKBACK_DAYS,
) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)

    yesterday = datetime.now(UTC).date() - timedelta(days=1)

    parser = argparse.ArgumentParser(description=f"Extract {report_type}, one file per day")
    parser.add_argument(
        "--start",
        type=date.fromisoformat,
        default=yesterday - timedelta(days=lookback_days - 1),
    )
    parser.add_argument("--end", type=date.fromisoformat, default=yesterday)
    args = parser.parse_args()

    if args.end > yesterday:
        parser.error("--end must be yesterday or earlier today. is not finished yet")

    config = SpApiConfig.from_env()
    client = SpApiClient(config)

    day = args.start
    while day <= args.end:
        extract_report_day(client, report_type, config.marketplace_ids, day, raw_dir, drop_columns)
        day += timedelta(days=1)

    client.close()