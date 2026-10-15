import json
from pathlib import Path

from amazon_elt.config import SpApiConfig
from amazon_elt.extract.runner import day_window, start_daily_run, write_day
from amazon_elt.spapi.client import SpApiClient
from amazon_elt.spapi.finances import list_transactions

RAW_DIR = Path("data/raw/finances")
# Deferred money is released days or weeks later, so each run re-pulls the last 30 days
LOOKBACK_DAYS = 30


def main() -> None:
    days = start_daily_run("Extract Finances transactions, one file per day", LOOKBACK_DAYS)

    config = SpApiConfig.from_env()
    client = SpApiClient(config)

    for day in days:
        start, end = day_window(day)
        transactions = list_transactions(client, config.marketplace_ids[0], start, end)

        rows = [{"transaction": json.dumps(t, sort_keys=True)} for t in transactions]
        write_day(rows, RAW_DIR, day)

    client.close()


if __name__ == "__main__":
    main()