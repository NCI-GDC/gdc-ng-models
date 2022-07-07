"""Data model to describe cohorts.

A cohort defines a set of cases that are of interest to a user. The concept
of a cohort is central to the user experience in the next-gen data portal. The
cohort data model includes the following entities:
    AnonymousContext: Used to authorize changes to a cohort
    Cohort: Defines the basic properties (name, id, context) of a cohort
    CohortFilter: Defines the filter used to generate a cohort case set
    CohortSnapshot: Defines the set of cases for a static cohort
"""

import uuid
import sqlalchemy
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext import declarative
from gdc_ng_models.models import audit

Base = declarative.declarative_base()


class AnonymousContext(Base, audit.AuditColumnsMixin):
    """An anonymous context to drive authorization for cohort manipulation.

    Provides authorization capabilities in lieu of a login (something the GDC
    data portal does not and cannot implement). When a cohort is created, it
    is associated with a context ID that establishes identity similar to a
    bearer token. When a request is made to manipulate a cohort, the context ID
    must be provided as part of that request to authorize a change.

    Attributes:
        id: A UUID identifier for the context.
        name: A human-readable name for the context.
        created_datetime: The date and time when the record is created.
        updated_datetime: The date and time when the record is updated.
    """

    __tablename__ = "anonymous_context"
    id = sqlalchemy.Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = sqlalchemy.Column(sqlalchemy.Text, nullable=False)

    # establishes a one-to-many relationship with Cohort
    cohorts = sqlalchemy.orm.relationship("Cohort")

    def __repr__(self):
        return (
            "<AnonymousContext("
            "id={id}, "
            "name='{name}', "
            "created_datetime={created_datetime}, "
            "updated_datetime={updated_datetime})>".format(
                id=self.id,
                name=self.name,
                created_datetime=self.created_datetime.isoformat() if self.created_datetime else None,
                updated_datetime=self.updated_datetime.isoformat() if self.updated_datetime else None,
            )
        )

    def to_json(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "created_datetime": self.created_datetime.isoformat() if self.created_datetime else None,
            "updated_datetime": self.updated_datetime.isoformat() if self.updated_datetime else None,
        }


class Cohort(Base, audit.AuditColumnsMixin):
    """A base definition for a cohort entity.

    Attributes:
        id: A UUID identifier for the cohort.
        context_id: The UUID of the associated context.
        name: A user defined name for the cohort.
        created_datetime: The date and time when the record is created.
        updated_datetime: The date and time when the record is updated.
    """

    __tablename__ = "cohort"
    id = sqlalchemy.Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    context_id = sqlalchemy.Column(postgresql.UUID(as_uuid=True), sqlalchemy.ForeignKey("anonymous_context.id"), nullable=False)

    # establishes a one-to-many relationship with CohortFilter
    filters = sqlalchemy.orm.relationship("CohortFilter")

    def __repr__(self):
        return (
            "<Cohort("
            "id={id}, "
            "name='{name}', "
            "context_id={context_id}, "
            "created_datetime={created_datetime}, "
            "updated_datetime={updated_datetime})>".format(
                id=self.id,
                name=self.name,
                context_id=self.context_id,
                created_datetime=self.created_datetime.isoformat() if self.created_datetime else None,
                updated_datetime=self.updated_datetime.isoformat() if self.updated_datetime else None,
            )
        )

    def to_json(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "context_id": str(self.context_id),
            "created_datetime": self.created_datetime.isoformat() if self.created_datetime else None,
            "updated_datetime": self.updated_datetime.isoformat() if self.updated_datetime else None,
        }


class CohortFilter(Base, audit.AuditColumnsMixin):
    """A filter defining the set of cases in a cohort.

    Provides the properties for defining a cohort filter, including the filter
    itself, a static indicator, and a self-referential foreign key to maintain
    a history of changes.

    Attributes:
        id: A bigint identifier for the cohort.
        parent_id: A self-referential key to maintain parent-child history.
        cohort_id: The ID of the cohort associated with the filter.
        filters: A JSONB representation of the filter defining the case set
        static: A boolean indicator to designate a filter as static.
        created_datetime: The date and time when the record is created.
        updated_datetime: The date and time when the record is updated.
    """

    __tablename__ = "cohort_filter"
    id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True)
    parent_id = sqlalchemy.Column(sqlalchemy.BigInteger, sqlalchemy.ForeignKey("cohort_filter.id"))
    cohort_id = sqlalchemy.Column(postgresql.UUID(as_uuid=True), sqlalchemy.ForeignKey("cohort.id"), nullable=False)
    filters = sqlalchemy.Column(postgresql.JSONB, nullable=False)
    static = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)

    # establishes a one-to-many relationship with CohortSnapshot
    snapshots = sqlalchemy.orm.relationship("CohortSnapshot")

    # establishes an adjacency relationship (i.e. self-referential key)
    parent = sqlalchemy.orm.relationship("CohortFilter")

    def __repr__(self):
        return (
            "<CohortFilter("
            "id={id}, "
            "parent_id={parent_id}, "
            "cohort_id={cohort_id}, "
            "filters={filters}, "
            "static={static}, "
            "created_datetime={created_datetime}, "
            "updated_datetime={updated_datetime})>".format(
                id=self.id,
                parent_id=self.parent_id,
                cohort_id=self.cohort_id,
                filters=self.filters,
                static=self.static,
                created_datetime=self.created_datetime.isoformat() if self.created_datetime else None,
                updated_datetime=self.updated_datetime.isoformat() if self.updated_datetime else None,
            )
        )

    def to_json(self):
        return {
            "id": self.id,
            "parent_id": self.parent_id,
            "cohort_id": str(self.cohort_id),
            "filters": self.filters,
            "static": self.static,
            "created_datetime": self.created_datetime.isoformat() if self.created_datetime else None,
            "updated_datetime": self.updated_datetime.isoformat() if self.updated_datetime else None,
        }


class CohortSnapshot(Base, audit.AuditColumnsMixin):
    """A static snapshot of cases associated with a cohort filter.

    In the event a cohort is static, this provides a list of cases associated
    with the cohort and the data release in which they were generated.

    Attributes:
        id: A bigint identifier for the snapshot.
        filter_id: The ID of the filter associated with the snapshot.
        data_release: The UUID of the data release when the snapshot was created.
        case_ids: A UUID array containing the set of case IDs.
        created_datetime: The date and time when the record is created.
        updated_datetime: The date and time when the record is updated.
    """

    __tablename__ = "cohort_snapshot"
    id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True)
    filter_id = sqlalchemy.Column(sqlalchemy.BigInteger, sqlalchemy.ForeignKey("cohort_filter.id"), nullable=False)
    data_release = sqlalchemy.Column(postgresql.UUID(as_uuid=True), nullable=False)
    case_ids = sqlalchemy.Column(postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=False)

    def __repr__(self):
        return (
            "<CohortSnapshot("
            "id={id}, "
            "filter_id={filter_id}, "
            "data_release={data_release}, "
            "case_ids={case_ids}, "
            "created_datetime={created_datetime}, "
            "updated_datetime={updated_datetime})>".format(
                id=self.id,
                filter_id=self.filter_id,
                data_release=self.data_release,
                case_ids=self.case_ids,
                created_datetime=self.created_datetime.isoformat() if self.created_datetime else None,
                updated_datetime=self.updated_datetime.isoformat() if self.updated_datetime else None,
            )
        )

    def to_json(self):
        return {
            "id": self.id,
            "filter_id": self.filter_id,
            "data_release": str(self.data_release),
            "case_ids": [str(case_id) for case_id in self.case_ids],
            "created_datetime": self.created_datetime.isoformat() if self.created_datetime else None,
            "updated_datetime": self.updated_datetime.isoformat() if self.updated_datetime else None,
        }
