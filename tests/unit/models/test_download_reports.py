import random

import pytest

from gdc_ng_models.models import download_reports

SIZE = "downloaded_size_gb"
COUNT = "user_interest_files_count"


def test__download_report__add_count_access_location() -> None:
    report = download_reports.DataDownloadReport()
    key = "germany"
    value = random.randint(1, 10)

    report.add_count_access_location(key, value)
    report.add_count_access_location(key, value)

    assert key in report.access_location_report and COUNT in report.access_location_report[key]
    assert report.access_location_report[key][COUNT] == value


def test__download_report__add_count_access_type() -> None:
    report = download_reports.DataDownloadReport()
    key = "delete"
    value = random.randint(1, 10)

    report.add_count_access_type(key, value)
    report.add_count_access_type(key, value)

    assert key in report.access_type_report and COUNT in report.access_type_report[key]
    assert report.access_type_report[key][COUNT] == value


def test__download_report__add_count_experimental_strategy() -> None:
    report = download_reports.DataDownloadReport()
    key = "WXS"
    value = random.randint(1, 10)

    report.add_count_experimental_strategy(key, value)
    report.add_count_experimental_strategy(key, value)

    assert (
        key in report.experimental_strategy_report
        and COUNT in report.experimental_strategy_report[key]
    )
    assert report.experimental_strategy_report[key][COUNT] == value


def test__download_report__add_count_project_id() -> None:
    report = download_reports.DataDownloadReport()
    key = "NCI-TEST"
    value = random.randint(1, 10)

    report.add_count_project_id(key, value)
    report.add_count_project_id(key, value)

    assert key in report.project_id_report and COUNT in report.project_id_report[key]
    assert report.project_id_report[key][COUNT] == value


def test__download_report__add_size_access_location() -> None:
    report = download_reports.DataDownloadReport()
    key = "china"
    value = random.randint(1, 10) / 10.0

    report.add_size_access_location(key, value)
    report.add_size_access_location(key, value)

    assert key in report.access_location_report and SIZE in report.access_location_report[key]
    assert report.access_location_report[key][SIZE] == pytest.approx(value)


def test__download_report__add_size_access_type() -> None:
    report = download_reports.DataDownloadReport()
    key = "download"
    value = random.randint(1, 10) / 10.0

    report.add_size_access_type(key, value)
    report.add_size_access_type(key, value)

    assert key in report.access_type_report and SIZE in report.access_type_report[key]
    assert report.access_type_report[key][SIZE] == pytest.approx(value)


def test__download_report__add_size_experimental_strategy() -> None:
    report = download_reports.DataDownloadReport()
    key = "WGS"
    value = random.randint(1, 10) / 10.0

    report.add_size_experimental_strategy(key, value)
    report.add_size_experimental_strategy(key, value)

    assert (
        key in report.experimental_strategy_report
        and SIZE in report.experimental_strategy_report[key]
    )
    assert report.experimental_strategy_report[key][SIZE] == pytest.approx(value)


def test__download_report__add_size_project_id() -> None:
    report = download_reports.DataDownloadReport()
    key = "GDC-TEST"
    value = random.randint(1, 10) / 10.0

    report.add_size_project_id(key, value)
    report.add_size_project_id(key, value)

    assert key in report.project_id_report and SIZE in report.project_id_report[key]
    assert report.project_id_report[key][SIZE] == pytest.approx(value)
