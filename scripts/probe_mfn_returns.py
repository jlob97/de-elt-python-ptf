from datetime import UTC, datetime, timedelta
from collections import Counter

from amazon_elt.config import SpApiConfig
from amazon_elt.spapi.client import SpApiClient
from amazon_elt.spapi.reports import fetch_report, parse_flat_file

REPORT_TYPE = "GET_FLAT_FILE_RETURNS_DATA_BY_RETURN_DATE"
US = "ATVPDKIKX0DER"

client = SpApiClient(SpApiConfig.from_env())
end = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
start = end - timedelta(days=30)

rows = parse_flat_file(fetch_report(client, REPORT_TYPE, [US], start, end))
print(f"\n=== US, last 30 days: {len(rows)} rows ===")
if rows:
    print("columns:", list(rows[0].keys()))
    for column in ["Order date", "Return request date"]:
        days = [
            datetime.strptime(r[column].strip(), "%d-%b-%Y").date()
            for r in rows
            if r[column].strip()
        ]
        print(f"{column}: {min(days)} -> {max(days)}")
    print("currency:", Counter(r["Currency code"] for r in rows))
    print("return type:", Counter(r["Return type"] for r in rows))