import csv
import gzip
import io
import logging
import time
from datetime import datetime

import httpx
from pydantic import BaseModel, Field

from amazon_elt.spapi.client import SpApiClient

logger = logging.getLogger(__name__)

REPORTS_PATH = "/reports/2021-06-30"
POLL_SECONDS = 30
MAX_WAIT_SECONDS = 30 * 60


class Report(BaseModel):
    report_id: str = Field(alias="reportId")
    processing_status: str = Field(alias="processingStatus")
    report_document_id: str | None = Field(default=None, alias="reportDocumentId")


class ReportDocument(BaseModel):
    url: str
    compression_algorithm: str | None = Field(default=None, alias="compressionAlgorithm")


def create_report(
    client: SpApiClient,
    report_type: str,
    marketplace_ids: list[str],
    start: datetime,
    end: datetime,
) -> str:
    body = {
        "reportType": report_type,
        "marketplaceIds": marketplace_ids,
        "dataStartTime": start.isoformat(),
        "dataEndTime": end.isoformat(),
    }
    response = client.request("POST", f"{REPORTS_PATH}/reports", "createReport", json=body)
    return response.json()["reportId"]


def wait_for_report(client: SpApiClient, report_id: str) -> Report:
    deadline = time.monotonic() + MAX_WAIT_SECONDS

    while True:
        response = client.request("GET", f"{REPORTS_PATH}/reports/{report_id}", "getReport")
        report = Report.model_validate(response.json())

        if report.processing_status == "DONE":
            return report
        if report.processing_status in ("CANCELLED", "FATAL"):
            raise RuntimeError(f"Report {report_id} ended as {report.processing_status}")
        if time.monotonic() > deadline:
            raise TimeoutError(f"Report {report_id} not ready after {MAX_WAIT_SECONDS}s")

        logger.info(
            "Report %s is %s, checking again in %ds",
            report_id, report.processing_status, POLL_SECONDS,
        )
        time.sleep(POLL_SECONDS)


def download_report(client: SpApiClient, report_document_id: str) -> bytes:
    response = client.request(
        "GET", f"{REPORTS_PATH}/documents/{report_document_id}", "getReportDocument"
    )
    document = ReportDocument.model_validate(response.json())

    # The URL is a pre-signed S3 link: it carries its own permission, no token
    file_response = httpx.get(document.url, timeout=120.0)
    file_response.raise_for_status()

    if document.compression_algorithm == "GZIP":
        return gzip.decompress(file_response.content)
    return file_response.content


def fetch_report(
    client: SpApiClient,
    report_type: str,
    marketplace_ids: list[str],
    start: datetime,
    end: datetime,
) -> bytes:
    report_id = create_report(client, report_type, marketplace_ids, start, end)
    logger.info("Created report %s (%s)", report_id, report_type)

    report = wait_for_report(client, report_id)
    if report.report_document_id is None:
        raise RuntimeError(f"Report {report_id} is DONE but has no document id")

    return download_report(client, report.report_document_id)

def parse_flat_file(data: bytes) -> list[dict[str, str]]:
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = data.decode("cp1252")

    reader = csv.DictReader(io.StringIO(text), delimiter="\t", quoting=csv.QUOTE_NONE)
    return list(reader)