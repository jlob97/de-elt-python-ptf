from collections import Counter
from datetime import UTC, datetime, timedelta
from typing import Any

from amazon_elt.config import SpApiConfig
from amazon_elt.spapi.client import SpApiClient

PATH = "/finances/2024-06-19/transactions"
US = "ATVPDKIKX0DER"

client = SpApiClient(SpApiConfig.from_env())
end = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
start = end - timedelta(days=7)

for label, marketplace in [("with marketplaceId=US", US), ("without marketplaceId", None)]:
    params: dict[str, Any] = {"postedAfter": start.isoformat(), "postedBefore": end.isoformat()}
    if marketplace:
        params["marketplaceId"] = marketplace

    transactions: list[dict[str, Any]] = []
    pages = 0
    while True:
        response = client.request("GET", PATH, "listTransactions", params=params)
        payload = response.json()["payload"]
        transactions.extend(payload.get("transactions", []))
        pages += 1
        next_token = payload.get("nextToken")
        if not next_token:
            break
        params["nextToken"] = next_token

    print(f"\n=== {label}: {len(transactions)} transactions in {pages} pages ===")
    if transactions:
        print("keys:", list(transactions[0].keys()))
        print("type:", Counter(t.get("transactionType") for t in transactions))
        print("status:", Counter(t.get("transactionStatus") for t in transactions))
        print("description:", Counter(t.get("description") for t in transactions))
        print("marketplace:", Counter(
            (t.get("marketplaceDetails") or {}).get("marketplaceName") for t in transactions
        ))
        posted = sorted(t["postedDate"] for t in transactions)
        print("postedDate:", posted[0], "->", posted[-1])