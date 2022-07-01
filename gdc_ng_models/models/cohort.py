"""Data model to describe cohorts.

A cohort defines a set of cases that are of interest to a user. The concept
of a cohort is central to the user experience in the next-gen data portal. A
cohort is defined by a filter that filters eligible cases based on demographic,
clinical or other relevant data points in a case.

This model defines the properties necessary to persist cohorts.
"""
import uuid

from sqlalchemy import orm, BigInteger, Boolean, Column, ForeignKey, Text
from sqlalchemy.ext import declarative
from sqlalchemy.dialects.postgresql import JSONB, UUID
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
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)

    # establishes a one-to-many relationship with Cohort
    cohorts = orm.relationship("Cohort")

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
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    context_id = Column(UUID(as_uuid=True), ForeignKey("anonymous_context.id"), nullable=False)

    # establishes a one-to-many relationship with CohortFilter
    filters = orm.relationship("CohortFilter")

    def __repr__(self):
        return (
            "<Cohort("
            "id={id}, "
            "name='{name}', "
            "context_id={context_id}, "
            # "current_filter_id={current_filter_id}, "
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
    id = Column(BigInteger, primary_key=True)
    parent_id = Column(BigInteger, ForeignKey("cohort_filter.id"))
    cohort_id = Column(UUID(as_uuid=True), ForeignKey("cohort.id"), nullable=False)
    filters = Column(JSONB, nullable=False)
    static = Column(Boolean, nullable=False, default=False)

    # establishes an adjacency relationship (i.e. self-referential key)
    # TODO: do we actually need make this to be one-to-one as per the design?
    parent = orm.relationship("CohortFilter")

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


# class CohortSnapshot(Base, audit.AuditColumnsMixin):
#     pass
