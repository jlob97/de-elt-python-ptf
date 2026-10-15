from typing import Any

from amazon_elt.config import SpApiConfig
from amazon_elt.spapi.client import SpApiClient

PATH = "/fba/inventory/v1/summaries"
US = "ATVPDKIKX0DER"

client = SpApiClient(SpApiConfig.from_env())

params: dict[str, Any] = {
    "granularityType": "Marketplace",
    "granularityId": US,
    "marketplaceIds": US,
    "details": "true",
}
summaries: list[dict[str, Any]] = []
pages = 0
while True:
    response = client.request("GET", PATH, "getInventorySummaries", params=params)
    body = response.json()
    summaries.extend(body["payload"].get("inventorySummaries", []))
    pages += 1
    next_token = (body.get("pagination") or {}).get("nextToken")
    if not next_token:
        break
    params["nextToken"] = next_token

print(f"\n=== {len(summaries)} SKUs in {pages} pages ===")
if summaries:
    print("keys:", list(summaries[0].keys()))
    print("inventoryDetails keys:", list((summaries[0].get("inventoryDetails") or {}).keys()))
    total = sum(s.get("totalQuantity", 0) for s in summaries)
    zero = sum(1 for s in summaries if s.get("totalQuantity", 0) == 0)
    print(f"total units: {total} | SKUs at zero: {zero}")
    print("lastUpdatedTime sample:", summaries[0].get("lastUpdatedTime"))