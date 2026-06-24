import json

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.dialects import postgresql

Base = orm.declarative_base()


DEFAULT_USAGE_REPORT = dict(visits=0, visitors=0, requests=0, network_usage=0)


class DataUsageReport(Base):
    __tablename__ = "data_usage_report"

    report_period = sqlalchemy.Column(
        sqlalchemy.Date, primary_key=True, nullable=False
    )  # MM/YYYY 01/31/2019

    api_report = sqlalchemy.Column(
        postgresql.JSONB, nullable=False, default=DEFAULT_USAGE_REPORT
    )

    portal_report = sqlalchemy.Column(
        postgresql.JSONB, nullable=False, default=DEFAULT_USAGE_REPORT
    )

    website_report = sqlalchemy.Column(
        postgresql.JSONB, nullable=False, default=DEFAULT_USAGE_REPORT
    )

    doc_site_report = sqlalchemy.Column(
        postgresql.JSONB, nullable=False, default=DEFAULT_USAGE_REPORT
    )

    date_created = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        nullable=False,
        server_default=sqlalchemy.text("now()"),
    )
    last_updated = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        nullable=False,
        server_default=sqlalchemy.text("now()"),
    )

    def set_api_report(self, visits, visitors, requests, network_usage):
        self.api_report = dict(
            visits=visits,
            visitors=visitors,
            requests=requests,
            network_usage=network_usage,
        )

    def set_portal_report(self, visits, visitors, requests, network_usage):
        self.portal_report = dict(
            visits=visits,
            visitors=visitors,
            requests=requests,
            network_usage=network_usage,
        )

    def set_website_report(self, visits, visitors, requests, network_usage):
        self.website_report = dict(
            visits=visits,
            visitors=visitors,
            requests=requests,
            network_usage=network_usage,
        )

    def set_doc_site_report(self, visits, visitors, requests, network_usage):
        self.doc_site_report = dict(
            visits=visits,
            visitors=visitors,
            requests=requests,
            network_usage=network_usage,
        )

    def to_json(self) -> dict:
        """Converts the object to a JSON safe dictionary.

        Returns:
            A dictionary w/ values which are JSON compatible.
        """
        return json.loads(
            json.dumps(
                {
                    "report_period": str(self.report_period),
                    "api_report": self.api_report,
                    "portal_report": self.portal_report,
                    "website_report": self.website_report,
                    "doc_site_report": self.doc_site_report,
                    "date_created": str(self.date_created),
                    "last_updated": str(self.last_updated),
                }
            )
        )


SIZE_FIELD = "downloaded_size_gb"
COUNT_FIELD = "user_interest_files_count"


class DataDownloadReport(Base):
    __tablename__ = "data_download_report"

    @staticmethod
    def _create_default():
        return {SIZE_FIELD: 0, COUNT_FIELD: 0}

    report_period = sqlalchemy.Column(sqlalchemy.Date, primary_key=True, nullable=False)

    project_id_report = sqlalchemy.Column(
        postgresql.JSONB, nullable=False, server_default="{}"
    )

    experimental_strategy_report = sqlalchemy.Column(
        postgresql.JSONB, nullable=False, server_default="{}"
    )

    access_type_report = sqlalchemy.Column(
        postgresql.JSONB, nullable=False, server_default="{}"
    )

    access_location_report = sqlalchemy.Column(
        postgresql.JSONB, nullable=False, server_default="{}"
    )

    date_created = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        nullable=False,
        server_default=sqlalchemy.text("now()"),
    )
    last_updated = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        nullable=False,
        server_default=sqlalchemy.text("now()"),
    )

    def add_size_access_type(self, access_type: str, size: float) -> None:
        """Updates the size of data associated with the given access type to the given value.

        Args:
            access_type: The type of data accessed: open/closed.
            size: The size in GB.
        """
        if not self.access_type_report:
            self.access_type_report = {}
        if access_type not in self.access_type_report:
            self.access_type_report[access_type] = DataDownloadReport._create_default()
        self.access_type_report[access_type][SIZE_FIELD] = size

    def add_size_experimental_strategy(self, strategy: str, size: float) -> None:
        """Updates the size of data associated with the given exp strategy to the given value.

        Args:
            strategy: The experimental strategy associated with the data accessed.
            size: The size in GB.
        """
        if not self.experimental_strategy_report:
            self.experimental_strategy_report = {}
        if strategy not in self.experimental_strategy_report:
            self.experimental_strategy_report[strategy] = DataDownloadReport._create_default()
        self.experimental_strategy_report[strategy][SIZE_FIELD] = size

    def add_size_project_id(self, project: str, size: float) -> None:
        """Updates the size of data associated with the given project ID to the given value.

        Args:
            project: The project ID associated with the data that was accessed.
            size: The size in GB.
        """
        if not self.project_id_report:
            self.project_id_report = {}
        if project not in self.project_id_report:
            self.project_id_report[project] = DataDownloadReport._create_default()
        self.project_id_report[project][SIZE_FIELD] = size

    def add_size_access_location(self, location: str, size: float) -> None:
        """Updates the size of data associated with the given location to the given value.

        Args:
            location: The country code from where the data was accessed.
            size: The size in GB.
        """
        if not self.access_location_report:
            self.access_location_report = {}
        if location not in self.access_location_report:
            self.access_location_report[location] = DataDownloadReport._create_default()
        self.access_location_report[location][SIZE_FIELD] = size

    def add_count_access_type(self, access_type: str, count: int) -> None:
        """Updates the count of files associated with the given access type to the given value.

        Args:
            access_type: The type of data accessed: open/closed.
            count: The number of files accessed.
        """
        if not self.access_type_report:
            self.access_type_report = {}
        if access_type not in self.access_type_report:
            self.access_type_report[access_type] = DataDownloadReport._create_default()
        self.access_type_report[access_type][COUNT_FIELD] = count

    def add_count_experimental_strategy(self, strategy: str, count: int) -> None:
        """Updates the count of files associated w/ the given exp strategy to the given value.

        Args:
            strategy: The experimental strategy associated with the data accessed.
            count: The number of files accessed.
        """
        if not self.experimental_strategy_report:
            self.experimental_strategy_report = {}
        if strategy not in self.experimental_strategy_report:
            self.experimental_strategy_report[strategy] = DataDownloadReport._create_default()
        self.experimental_strategy_report[strategy][COUNT_FIELD] = count

    def add_count_project_id(self, project: str, count: int) -> None:
        """Updates the count of files associated with the given project ID to the given value.

        Args:
            project: The project ID associated with the data that was accessed.
            count: The number of files accessed.
        """
        if not self.project_id_report:
            self.project_id_report = {}
        if project not in self.project_id_report:
            self.project_id_report[project] = DataDownloadReport._create_default()
        self.project_id_report[project][COUNT_FIELD] = count

    def add_count_access_location(self, location: str, count: int) -> None:
        """Updates the count of files associated with the given location to the given value.

        Args:
            location: The country code from where the data was accessed.
            count: The number of files accessed.
        """
        if not self.access_location_report:
            self.access_location_report = {}
        if location not in self.access_location_report:
            self.access_location_report[location] = DataDownloadReport._create_default()
        self.access_location_report[location][COUNT_FIELD] = count

    def to_json(self) -> dict:
        """Converts the object to a JSON safe dictionary.

        Returns:
            A dictionary w/ values which are JSON compatible.
        """
        return json.loads(
            json.dumps(
                {
                    "report_period": str(self.report_period),
                    "project_id_report": self.project_id_report,
                    "experimental_strategy_report": self.experimental_strategy_report,
                    "access_type_report": self.access_type_report,
                    "access_location_report": self.access_location_report,
                    "date_created": str(self.date_created),
                    "last_updated": str(self.last_updated),
                }
            )
        )


class MonthlyAwstats(Base):
    __tablename__ = "monthly_awstats"
    report_date = sqlalchemy.Column("date", sqlalchemy.Date, primary_key=True)
    site = sqlalchemy.Column("site", sqlalchemy.String(length=50), primary_key=True)
    # TODO: many of these are currently Integers, should they be BigInts?
    unique_visitors = sqlalchemy.Column("unique_visitors", sqlalchemy.Integer)
    number_of_visits = sqlalchemy.Column("number_of_visits", sqlalchemy.Integer)
    viewed_pages = sqlalchemy.Column("viewed_pages", sqlalchemy.Integer)
    viewed_hits = sqlalchemy.Column("viewed_hits", sqlalchemy.Integer)
    viewed_bw_gb = sqlalchemy.Column("viewed_bw_gb", sqlalchemy.Float)
    unviewed_pages = sqlalchemy.Column("unviewed_pages", sqlalchemy.Integer)
    unviewed_hits = sqlalchemy.Column("unviewed_hits", sqlalchemy.Integer)
    unviewed_bw_gb = sqlalchemy.Column("unviewed_bw_gb", sqlalchemy.Float)
    observium_bw_in_gb = sqlalchemy.Column("observium_bw_in_gb", sqlalchemy.Float)
    observium_bw_out_gb = sqlalchemy.Column("observium_bw_out_gb", sqlalchemy.Float)
