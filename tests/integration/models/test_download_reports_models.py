import json
from datetime import date

import pytest
from cdisutils.dictionary import sort_dict

from gdc_ng_models.models.download_reports import DataDownloadReport, DataUsageReport


def test_create_usage_reports(create_reports_db, db_session):

    report = DataUsageReport()
    report.set_api_report(visits=10, visitors=1, requests=100, network_usage=100.0)
    report.set_portal_report(visits=10, visitors=3, requests=100, network_usage=120.0)
    report.set_doc_site_report(visits=10, visitors=4, requests=100, network_usage=10.0)
    report.set_website_report(visits=10, visitors=1, requests=100, network_usage=100.0)
    report.report_period = date.today()

    db_session.add(report)
    db_session.commit()

    # check if persisted
    rp = (
        db_session.query(DataUsageReport)
        .filter(DataUsageReport.report_period == report.report_period)
        .first()
    )

    assert rp.api_report == report.api_report
    assert rp.report_period == report.report_period
    assert sort_dict(rp.api_report) == sort_dict(report.api_report)
    assert sort_dict(rp.portal_report) == sort_dict(report.portal_report)
    assert sort_dict(rp.website_report) == sort_dict(report.website_report)
    assert sort_dict(rp.doc_site_report) == sort_dict(report.doc_site_report)
    assert rp.date_created == report.date_created
    assert rp.last_updated == report.last_updated


def test_create_download_report(create_reports_db, db_session):

    report = DataDownloadReport()

    report.add_size_access_type("open", 100.0)
    report.add_size_access_type("closed", 33.0)
    report.add_size_experimental_strategy("WXS", 100.0)
    report.add_size_access_location("San Francisco, CA, USA", 300)
    report.add_size_project_id("TCGA-YYY", 330)
    report.add_count_access_type("open", 10)
    report.add_count_access_type("closed", 3)
    report.add_count_experimental_strategy("WXS", 101)
    report.add_count_access_location("San Francisco, CA, USA", 303)
    report.add_count_project_id("TCGA-YYY", 3300)
    report.report_period = date.today()

    db_session.add(report)
    db_session.commit()

    # check if persisted
    rp = (
        db_session.query(DataDownloadReport)
        .filter(DataDownloadReport.report_period == report.report_period)
        .first()
    )

    assert rp.report_period == report.report_period
    assert sort_dict(rp.project_id_report) == sort_dict(report.project_id_report)
    assert sort_dict(rp.experimental_strategy_report) == sort_dict(
        report.experimental_strategy_report
    )
    assert sort_dict(rp.access_type_report) == sort_dict(report.access_type_report)
    assert sort_dict(rp.access_location_report) == sort_dict(report.access_location_report)
    assert rp.project_id_report == report.project_id_report
    assert rp.date_created == report.date_created
    assert rp.last_updated == report.last_updated


def test_download_report_to_json_contains_size_and_count():

    report = DataDownloadReport()

    report.add_size_access_type("open", 100.0)
    report.add_size_experimental_strategy("WXS", 101.0)
    report.add_size_project_id("TCGA-YYY", 330)
    report.add_count_access_type("closed", 3)
    report.add_count_access_location("San Francisco, CA, USA", 303)

    assert report.to_json() == json.loads(
        """
        {
            "access_type_report": {
                "open": {
                    "downloaded_size_gb": 100.0,
                    "user_interest_files_count": 0
                },
                "closed": {
                    "downloaded_size_gb": 0,
                    "user_interest_files_count": 3
                }
            },
            "experimental_strategy_report": {
                "WXS": {
                    "downloaded_size_gb": 101.0,
                    "user_interest_files_count": 0
                }
            },
            "project_id_report": {
                "TCGA-YYY": {
                    "downloaded_size_gb": 330.0,
                    "user_interest_files_count": 0
                }
            },
            "access_location_report": {
                "San Francisco, CA, USA": {
                    "downloaded_size_gb": 0,
                    "user_interest_files_count": 303
                }
            },
            "report_period": "None",
            "date_created": "None",
            "last_updated": "None"
        }
        """
    )


_SIZE_COUNT_PROP_MAP = {
    "size": "downloaded_size_gb",
    "count": "user_interest_files_count",
}


@pytest.mark.parametrize("size_or_count", (("size", "count")))
@pytest.mark.parametrize(
    "field_name",
    ("access_type", "project_id", "access_location", "experimental_strategy"),
)
def test_download_report_to_json_contains_field_with_value(field_name, size_or_count):
    report = DataDownloadReport()
    adder_method = getattr(report, f"add_{size_or_count}_{field_name}")

    adder_method(field_name, 123)
    assert report.to_json() == json.loads(
        f"""
        {
            "{field_name}_report": {
                "{_SIZE_COUNT_PROP_MAP[size_or_count]}": 123
            }
        }
        """
    )
