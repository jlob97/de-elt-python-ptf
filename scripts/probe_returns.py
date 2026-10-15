from collections import Counter
from datetime import UTC, datetime, timedelta

from amazon_elt.config import SpApiConfig
from amazon_elt.spapi.client import SpApiClient
from amazon_elt.spapi.reports import fetch_report, parse_flat_file

REPORT_TYPE = "GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA"
US = "ATVPDKIKX0DER"

client = SpApiClient(SpApiConfig.from_env())
end = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
start = end - timedelta(days=7)

rows = parse_flat_file(fetch_report(client, REPORT_TYPE, [US], start, end))
print(f"\n=== US: {len(rows)} rows ===")
if rows:
    print("columns:", list(rows[0].keys()))
    print("return-date range:", min(r["return-date"] for r in rows), "->",
          max(r["return-date"] for r in rows))
    print("fulfillment centers:", Counter(r["fulfillment-center-id"] for r in rows))
    print("status:", Counter(r["status"] for r in rows))