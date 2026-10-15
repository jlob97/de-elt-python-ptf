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


def day_window(day: date) -> tuple[datetime, datetime]:
    # One UTC day: from 00:00 to the next day's 00:00
    start = datetime.combine(day, time(0), tzinfo=UTC)
    return start, start + timedelta(days=1)


def write_day(rows: list[dict[str, str]], raw_dir: Path, day: date) -> None:
    path = raw_dir / f"dt={day.isoformat()}" / f"{raw_dir.name}.parquet"
    write_parquet(rows, path)
    logger.info("Wrote %d rows to %s", len(rows), path)


def setup_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    # httpx logs every URL at INFO, and report download URLs are pre-signed S3 links
    logging.getLogger("httpx").setLevel(logging.WARNING)


def start_daily_run(description: str, lookback_days: int = LOOKBACK_DAYS) -> list[date]:
    # Turns on logging and reads --start/--end. Returns the days to extract
    setup_logging()

    yesterday = datetime.now(UTC).date() - timedelta(days=1)

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--start",
        type=date.fromisoformat,
        default=yesterday - timedelta(days=lookback_days - 1),
    )
    parser.add_argument("--end", type=date.fromisoformat, default=yesterday)
    args = parser.parse_args()

    if args.end > yesterday:
        parser.error("--end must be yesterday or earlier (today is not finished yet)")

    days = []
    day = args.start
    while day <= args.end:
        days.append(day)
        day += timedelta(days=1)
    return days


def extract_report_day(
    client: SpApiClient,
    report_type: str,
    marketplace_ids: list[str],
    day: date,
    raw_dir: Path,
    drop_columns: tuple[str, ...] = (),
) -> None:
    start, end = day_window(day)

    data = fetch_report(client, report_type, marketplace_ids, start, end)
    rows = parse_flat_file(data)

    for row in rows:
        for column in drop_columns:
            row.pop(column, None)

    write_day(rows, raw_dir, day)


def run_report_stream(
    report_type: str,
    raw_dir: Path,
    drop_columns: tuple[str, ...] = (),
    lookback_days: int = LOOKBACK_DAYS,
) -> None:
    days = start_daily_run(f"Extract {report_type}, one file per day", lookback_days)

    config = SpApiConfig.from_env()
    client = SpApiClient(config)

    for day in days:
        extract_report_day(client, report_type, config.marketplace_ids, day, raw_dir, drop_columns)

    client.close()


def run_report_snapshot(report_type: str, raw_dir: Path) -> None:
    setup_logging()
    today = datetime.now(UTC).date()

    config = SpApiConfig.from_env()
    client = SpApiClient(config)

    # A snapshot report ignores dates, but createReport still wants a range: send the last day
    start, end = day_window(today - timedelta(days=1))
    rows = parse_flat_file(fetch_report(client, report_type, config.marketplace_ids, start, end))
    write_day(rows, raw_dir, today)

    client.close()
