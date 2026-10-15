"""One-off probe of the FBA amazon-fulfilled shipments report (2026-10-15).

Used to decide the design of the shipments stream: which date to partition on,
and which columns hold buyer personal data so the extractor can drop them.
Prints only column names and fill counts, never personal values.
"""

from collections import Counter
from datetime import UTC, datetime, timedelta

from amazon_elt.config import SpApiConfig
from amazon_elt.spapi.client import SpApiClient
from amazon_elt.spapi.reports import fetch_report, parse_flat_file

REPORT_TYPE = "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL"
US = "ATVPDKIKX0DER"
PERSONAL_HINTS = ("buyer", "recipient", "address", "phone", "email", "bill-", "ship-")

client = SpApiClient(SpApiConfig.from_env())
end = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
start = end - timedelta(days=7)

rows = parse_flat_file(fetch_report(client, REPORT_TYPE, [US], start, end))
print(f"\n=== {len(rows)} shipment lines in 7 days ===")
if rows:
    print("columns:", list(rows[0].keys()))
    print("\nPossibly personal columns -> how many rows have a value:")
    for column in rows[0]:
        if any(hint in column for hint in PERSONAL_HINTS):
            filled = sum(1 for r in rows if r[column].strip())
            print(f"  {column}: {filled}/{len(rows)}")
    shipment_days = sorted(r["shipment-date"][:10] for r in rows if r.get("shipment-date"))
    if shipment_days:
        print("\nshipment-date range:", shipment_days[0], "->", shipment_days[-1])
    print("sales-channel:", Counter(r.get("sales-channel") for r in rows))
