import json
import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB


Base = declarative_base()


DEFAULT_USAGE_REPORT = dict(
    visits=0,
    visitors=0,
    requests=0,
    network_usage=0
)


class DataUsageReport(Base):

    __tablename__ = "data_usage_report"

    report_period = db.Column(
        db.Date, primary_key=True, nullable=False)  # MM/YYYY 01/31/2019

    all_report = db.Column(
        JSONB, nullable=False, default=DEFAULT_USAGE_REPORT)

    api_report = db.Column(
        JSONB, nullable=False, default=DEFAULT_USAGE_REPORT)

    portal_report = db.Column(
        JSONB, nullable=False, default=DEFAULT_USAGE_REPORT)

    website_report = db.Column(
        JSONB, nullable=False, default=DEFAULT_USAGE_REPORT)

    doc_site_report = db.Column(
        JSONB, nullable=False, default=DEFAULT_USAGE_REPORT)

    date_created = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=db.text('now()'))
    last_updated = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=db.text('now()'))

    def set_all_report(self, visits, visitors, requests, network_usage):
        self.all_report = dict(
            visits=visits,
            visitors=visitors,
            requests=requests,
            network_usage=network_usage
        )

    def set_api_report(self, visits, visitors, requests, network_usage):
        self.api_report = dict(
            visits=visits,
            visitors=visitors,
            requests=requests,
            network_usage=network_usage
        )

    def set_portal_report(self, visits, visitors, requests, network_usage):
        self.portal_report = dict(
            visits=visits,
            visitors=visitors,
            requests=requests,
            network_usage=network_usage
        )

    def set_website_report(self, visits, visitors, requests, network_usage):
        self.website_report = dict(
            visits=visits,
            visitors=visitors,
            requests=requests,
            network_usage=network_usage
        )

    def set_doc_site_report(self, visits, visitors, requests, network_usage):
        self.doc_site_report = dict(
            visits=visits,
            visitors=visitors,
            requests=requests,
            network_usage=network_usage
        )

    def to_json(self):
        """Returns a JSON safe representation of :class:`DataUsageReport`"""

        return json.loads(json.dumps({
            'report_period': str(self.report_period),
            'all_report': self.all_report,
            'api_report': self.api_report,
            'portal_report': self.portal_report,
            'website_report': self.website_report,
            'doc_site_report': self.doc_site_report,
            'date_created': str(self.date_created),
            'last_updated': str(self.last_updated)
        }))


class DataDownloadReport(Base):

    __tablename__ = "data_download_report"

    report_period = db.Column(db.Date, primary_key=True, nullable=False)

    project_id_report = db.Column(JSONB, nullable=False, server_default='{}')

    experimental_strategy_report = db.Column(
        JSONB, nullable=False, server_default='{}')

    access_type_report = db.Column(JSONB, nullable=False, server_default='{}')

    access_location_report = db.Column(JSONB, nullable=False, server_default='{}')

    date_created = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=db.text('now()'))
    last_updated = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=db.text('now()'))

    def add_access_type(self, access_type, size):
        """
        Args:
            access_type (str): open/closed
            size (double): size in GB
        """
        if not self.access_type_report:
            self.access_type_report = {}
        self.access_type_report[access_type] = size

    def add_experimental_strategy(self, strategy, size):
        """
        Args:
            strategy (str): strategy name
            size (double): size in GB
        """
        if not self.experimental_strategy_report:
            self.experimental_strategy_report = {}
        self.experimental_strategy_report[strategy] = size

    def add_project_id(self, project, size):
        """
        Args:
            project id (str): project's name
            size (double): size in GB
        """
        if not self.project_id_report:
            self.project_id_report = {}
        self.project_id_report[project] = size

    def add_access_location(self, location, size):
        """
        Args:
            location (str): location name (country code)
            size (double): size in GB
        """
        if not self.access_location_report:
            self.access_location_report = {}
        self.access_location_report[location] = size

    def to_json(self):
        """Returns a JSON safe representation of :class:`DataDownloadReport`"""

        return json.loads(json.dumps({
            'report_period': str(self.report_period),
            'project_id_report': self.project_id_report,
            'experimental_strategy_report': self.experimental_strategy_report,
            'access_type_report': self.access_type_report,
            'access_location_report': self.access_location_report,
            'date_created': str(self.date_created),
            'last_updated': str(self.last_updated)
        }))


class MonthlyAwstats(Base):
    __tablename__ = 'monthly_awstats'
    report_date = db.Column('date', db.Date, primary_key=True)
    site = db.Column('site', db.String(length=50), primary_key=True)
    # TODO: many of these are currently Integers, should they be BigInts?
    unique_visitors = db.Column('unique_visitors', db.Integer)
    number_of_visits = db.Column('number_of_visits', db.Integer)
    viewed_pages = db.Column('viewed_pages', db.Integer)
    viewed_hits = db.Column('viewed_hits', db.Integer)
    viewed_bw_gb = db.Column('viewed_bw_gb', db.Float)
    unviewed_pages = db.Column('unviewed_pages', db.Integer)
    unviewed_hits = db.Column('unviewed_hits', db.Integer)
    unviewed_bw_gb = db.Column('unviewed_bw_gb', db.Float)
    observium_bw_in_gb = db.Column('observium_bw_in_gb', db.Float)
    observium_bw_out_gb = db.Column('observium_bw_out_gb', db.Float)
