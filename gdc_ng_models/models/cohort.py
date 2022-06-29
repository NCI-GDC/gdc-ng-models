"""Data model to describe cohorts.

A cohort defines a set of cases that are of interest to a user. The concept
of a cohort is central to the user experience in the next-gen data portal. A
cohort is defined by a filter that filters eligible cases based on demographic,
clinical or other relevant data points in a case.

This model defines the properties necessary to persist cohorts.
"""
import uuid

from sqlalchemy import BigInteger, Column, ForeignKey, orm, Text
from sqlalchemy.ext import declarative
from sqlalchemy.dialects.postgresql import UUID
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
    id = Column(UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)

    def __repr__(self):
        return f"<AnonymousContext(" \
               f"id={self.id}, " \
               f"name='{self.name}', " \
               f"created_datetime={self.created_datetime}, " \
               f"updated_datetime={self.updated_datetime})>"

    def to_json(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "created_datetime": self.created_datetime.isoformat() if self.created_datetime else None,
            "updated_datetime": self.updated_datetime.isoformat() if self.updated_datetime else None,
        }


# class Cohort(Base, audit.AuditColumnsMixin):
#     pass
#
#
# class CohortFilter(Base, audit.AuditColumnsMixin):
#     pass
#
#
# class CohortSnapshot(Base, audit.AuditColumnsMixin):
#     pass
