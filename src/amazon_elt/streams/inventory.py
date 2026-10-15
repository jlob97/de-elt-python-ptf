import json
from datetime import UTC, datetime
from pathlib import Path

from amazon_elt.config import SpApiConfig
from amazon_elt.extract.runner import setup_logging, write_day
from amazon_elt.spapi.client import SpApiClient
from amazon_elt.spapi.inventory import list_inventory_summaries

RAW_DIR = Path("data/raw/inventory")


def main() -> None:
    setup_logging()
    today = datetime.now(UTC).date()

    config = SpApiConfig.from_env()
    client = SpApiClient(config)

    summaries = list_inventory_summaries(client, config.marketplace_ids[0])
    rows = [{"summary": json.dumps(s, sort_keys=True)} for s in summaries]
    write_day(rows, RAW_DIR, today)

    client.close()


if __name__ == "__main__":
    main()