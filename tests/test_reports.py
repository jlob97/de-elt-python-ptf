from amazon_elt.spapi.reports import Report, ReportDocument


def test_report_document_reads_compression_algorithm() -> None:
    payload = {
        "reportDocumentId": "doc-1",
        "url": "https://example.com/report",
        "compressionAlgorithm": "GZIP",
    }

    document = ReportDocument.model_validate(payload)

    assert document.compression_algorithm == "GZIP"


def test_report_document_without_compression() -> None:
    payload = {"reportDocumentId": "doc-1", "url": "https://example.com/report"}

    document = ReportDocument.model_validate(payload)

    assert document.compression_algorithm is None


def test_report_in_queue_has_no_document_id() -> None:
    payload = {"reportId": "123", "processingStatus": "IN_QUEUE"}

    report = Report.model_validate(payload)

    assert report.report_id == "123"
    assert report.processing_status == "IN_QUEUE"
    assert report.report_document_id is None