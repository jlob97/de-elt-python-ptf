from typing import Any

from amazon_elt.spapi.client import SpApiClient

SUMMARIES_PATH = "/fba/inventory/v1/summaries"


def list_inventory_summaries(client: SpApiClient, marketplace_id: str) -> list[dict[str, Any]]:
    params: dict[str, Any] = {
        "granularityType": "Marketplace",
        "granularityId": marketplace_id,
        "marketplaceIds": marketplace_id,
        "details": "true",
    }
    summaries: list[dict[str, Any]] = []

    # Pages again, but here nextToken sits in "pagination", outside the payload
    while True:
        response = client.request("GET", SUMMARIES_PATH, "getInventorySummaries", params=params)
        body = response.json()
        summaries.extend(body["payload"].get("inventorySummaries", []))

        next_token = (body.get("pagination") or {}).get("nextToken")
        if not next_token:
            return summaries
        params["nextToken"] = next_token
