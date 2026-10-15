from collections import Counter
from datetime import UTC, datetime, timedelta

from amazon_elt.config import SpApiConfig
from amazon_elt.spapi.client import SpApiClient
from amazon_elt.spapi.reports import fetch_report, parse_flat_file

REPORT_TYPE = "GET_MERCHANT_LISTINGS_ALL_DATA"
US = "ATVPDKIKX0DER"

client = SpApiClient(SpApiConfig.from_env())
end = datetime.now(UTC).replace(microsecond=0)
start = end - timedelta(days=1)

rows = parse_flat_file(fetch_report(client, REPORT_TYPE, [US], start, end))
print(f"\n=== {len(rows)} listings ===")
if rows:
    print("columns:", list(rows[0].keys()))
    print("status:", Counter(r.get("status") for r in rows))
    print("fulfillment-channel:", Counter(r.get("fulfillment-channel") for r in rows))
    print("unique SKUs:", len({r.get("seller-sku") for r in rows}))
    open_dates = sorted(r["open-date"] for r in rows if r.get("open-date"))
    if open_dates:
        print("open-date sample (oldest, newest):", open_dates[0], "|", open_dates[-1])