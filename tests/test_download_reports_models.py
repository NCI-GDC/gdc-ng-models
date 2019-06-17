from datetime import date

from gdc_ng_models.models.download_reports import (
    DataDownloadReport,
    DataUsageReport,
)


def test_ping(db_session):
    assert True


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
    rp = db_session\
        .query(DataUsageReport)\
        .filter(DataUsageReport.report_period == report.report_period)\
        .first()

    assert rp.api_report == report.api_report
    assert rp.report_period == report.report_period
    assert rp.portal_report == report.portal_report


def test_create_download_report(create_reports_db, db_session):

    report = DataDownloadReport()

    report.add_access_type("open", 100.0)
    report.add_access_type("closed", 33.0)
    report.add_experimental_strategy("WXS", 100.0)
    report.add_access_location("San Francisco, CA, USA", 300)
    report.add_project_id("TCGA-YYY", 330)
    report.report_period = date.today()

    db_session.add(report)
    db_session.commit()

    # check if persisted
    rp = db_session\
        .query(DataDownloadReport)\
        .filter(DataDownloadReport.report_period == report.report_period)\
        .first()

    assert rp.access_location_report == report.access_location_report
    assert rp.report_period == report.report_period
    assert rp.project_id_report == report.project_id_report
