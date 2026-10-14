from datetime import UTC, datetime, timedelta

from amazon_elt.config import SpApiConfig
from amazon_elt.spapi.client import SpApiClient
from amazon_elt.spapi.reports import fetch_report

US_MARKETPLACE = "ATVPDKIKX0DER"
MX_MARKETPLACE = "A1AM78C64UM0Y8"

ORDERS_REPORT = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL"

# Columns the load step depends on. If Amazon drops or renames one, this test fails first.
ORDERS_REQUIRED_COLUMNS = {
    "amazon-order-id",
    "purchase-date",
    "last-updated-date",
    "order-status",
    "fulfillment-channel",
    "sales-channel",
    "sku",
    "asin",
    "quantity",
    "currency",
    "item-price",
}


def test_marketplaces_include_us_and_mx() -> None:
    client = SpApiClient(SpApiConfig.from_env())

    response = client.request(
        "GET", "/sellers/v1/marketplaceParticipations", "getMarketplaceParticipations"
    )
    marketplace_ids = {p["marketplace"]["id"] for p in response.json()["payload"]}

    assert {US_MARKETPLACE, MX_MARKETPLACE} <= marketplace_ids


def test_orders_report_has_required_columns() -> None:
    client = SpApiClient(SpApiConfig.from_env())
    end = datetime.now(UTC).replace(microsecond=0)
    start = end - timedelta(days=1)

    data = fetch_report(client, ORDERS_REPORT, [US_MARKETPLACE], start, end)
    header = data.decode("utf-8").splitlines()[0].split("\t")

    missing = ORDERS_REQUIRED_COLUMNS - set(header)
    assert not missing, f"Orders report is missing columns: {missing}"
