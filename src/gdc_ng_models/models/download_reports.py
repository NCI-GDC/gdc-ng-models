import json

import sqlalchemy as db
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


DEFAULT_USAGE_REPORT = dict(visits=0, visitors=0, requests=0, network_usage=0)


class DataUsageReport(Base):
    __tablename__ = "data_usage_report"

    report_period = db.Column(db.Date, primary_key=True, nullable=False)  # MM/YYYY 01/31/2019

    api_report = db.Column(JSONB, nullable=False, default=DEFAULT_USAGE_REPORT)

    portal_report = db.Column(JSONB, nullable=False, default=DEFAULT_USAGE_REPORT)

    website_report = db.Column(JSONB, nullable=False, default=DEFAULT_USAGE_REPORT)

    doc_site_report = db.Column(JSONB, nullable=False, default=DEFAULT_USAGE_REPORT)

    date_created = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=db.text("now()")
    )
    last_updated = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=db.text("now()")
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

    def to_json(self):
        """Returns a JSON safe representation of :class:`DataUsageReport`."""
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

    report_period = db.Column(db.Date, primary_key=True, nullable=False)

    project_id_report = db.Column(JSONB, nullable=False, server_default="{}")

    experimental_strategy_report = db.Column(JSONB, nullable=False, server_default="{}")

    access_type_report = db.Column(JSONB, nullable=False, server_default="{}")

    access_location_report = db.Column(JSONB, nullable=False, server_default="{}")

    date_created = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=db.text("now()")
    )
    last_updated = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=db.text("now()")
    )

    def add_size_access_type(self, access_type: str, size: float) -> None:
        """Adds the size to the given access type.

        Args:
            access_type: open/closed.
            size: size in GB.
        """
        if not self.access_type_report:
            self.access_type_report = {}
        if access_type not in self.access_type_report:
            self.access_type_report[access_type] = DataDownloadReport._create_default()
        self.access_type_report[access_type][SIZE_FIELD] = size

    def add_size_experimental_strategy(self, strategy: str, size: float) -> None:
        """Adds the size to the given strategy.

        Args:
            strategy: strategy name.
            size: size in GB.
        """
        if not self.experimental_strategy_report:
            self.experimental_strategy_report = {}
        if strategy not in self.experimental_strategy_report:
            self.experimental_strategy_report[strategy] = DataDownloadReport._create_default()
        self.experimental_strategy_report[strategy][SIZE_FIELD] = size

    def add_size_project_id(self, project: str, size: float) -> None:
        """Adds the size to the given project.

        Args:
            project: project's name.
            size: size in GB.
        """
        if not self.project_id_report:
            self.project_id_report = {}
        if project not in self.project_id_report:
            self.project_id_report[project] = DataDownloadReport._create_default()
        self.project_id_report[project][SIZE_FIELD] = size

    def add_size_access_location(self, location: str, size: float) -> None:
        """Adds the size to the given location.

        Args:
            location: location name (country code).
            size: size in GB.
        """
        if not self.access_location_report:
            self.access_location_report = {}
        if location not in self.access_location_report:
            self.access_location_report[location] = DataDownloadReport._create_default()
        self.access_location_report[location][SIZE_FIELD] = size

    def add_count_access_type(self, access_type: str, count: int) -> None:
        """Adds the count to the given access type.

        Args:
            access_type: open/closed.
            count: count.
        """
        if not self.access_type_report:
            self.access_type_report = {}
        if access_type not in self.access_type_report:
            self.access_type_report[access_type] = DataDownloadReport._create_default()
        self.access_type_report[access_type][COUNT_FIELD] = count

    def add_count_experimental_strategy(self, strategy: str, count: int) -> None:
        """Adds the count to the given experimental strategy.

        Args:
            strategy: strategy name.
            count: count.
        """
        if not self.experimental_strategy_report:
            self.experimental_strategy_report = {}
        if strategy not in self.experimental_strategy_report:
            self.experimental_strategy_report[strategy] = DataDownloadReport._create_default()
        self.experimental_strategy_report[strategy][COUNT_FIELD] = count

    def add_count_project_id(self, project: str, count: int) -> None:
        """Adds the count to the given project.

        Args:
            project: project's name.
            count: count.
        """
        if not self.project_id_report:
            self.project_id_report = {}
        if project not in self.project_id_report:
            self.project_id_report[project] = DataDownloadReport._create_default()
        self.project_id_report[project][COUNT_FIELD] = count

    def add_count_access_location(self, location: str, count: int) -> None:
        """Adds the count to the given location.

        Args:
            location: location name (country code).
            count: count.
        """
        if not self.access_location_report:
            self.access_location_report = {}
        if location not in self.access_location_report:
            self.access_location_report[location] = DataDownloadReport._create_default()
        self.access_location_report[location][COUNT_FIELD] = count

    def to_json(self) -> dict:
        """Converts the model to a json compatible dictionary.

        Returns:
            A JSON safe representation of :class:`DataDownloadReport`.
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
    report_date = db.Column("date", db.Date, primary_key=True)
    site = db.Column("site", db.String(length=50), primary_key=True)
    # TODO: many of these are currently Integers, should they be BigInts?
    unique_visitors = db.Column("unique_visitors", db.Integer)
    number_of_visits = db.Column("number_of_visits", db.Integer)
    viewed_pages = db.Column("viewed_pages", db.Integer)
    viewed_hits = db.Column("viewed_hits", db.Integer)
    viewed_bw_gb = db.Column("viewed_bw_gb", db.Float)
    unviewed_pages = db.Column("unviewed_pages", db.Integer)
    unviewed_hits = db.Column("unviewed_hits", db.Integer)
    unviewed_bw_gb = db.Column("unviewed_bw_gb", db.Float)
    observium_bw_in_gb = db.Column("observium_bw_in_gb", db.Float)
    observium_bw_out_gb = db.Column("observium_bw_out_gb", db.Float)
