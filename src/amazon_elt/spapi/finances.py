from datetime import datetime
from typing import Any

from amazon_elt.spapi.client import SpApiClient

TRANSACTIONS_PATH = "/finances/2024-06-19/transactions"


def list_transactions(
    client: SpApiClient,
    marketplace_id: str,
    start: datetime,
    end: datetime,
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {
        "postedAfter": start.isoformat(),
        "postedBefore": end.isoformat(),
        "marketplaceId": marketplace_id,
    }
    transactions: list[dict[str, Any]] = []

    # Amazon pages the answer: keep asking with nextToken until it stops sending one
    while True:
        response = client.request("GET", TRANSACTIONS_PATH, "listTransactions", params=params)
        payload = response.json()["payload"]
        transactions.extend(payload.get("transactions", []))

        next_token = payload.get("nextToken")
        if not next_token:
            return transactions
        params["nextToken"] = next_token