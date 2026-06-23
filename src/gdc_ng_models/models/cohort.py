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
from sqlalchemy import orm
from sqlalchemy.dialects import postgresql

from gdc_ng_models.models import accessed, audit

Base = orm.declarative_base()


class AnonymousContext(Base, audit.AuditColumnsMixin):
    """An anonymous context to drive authorization for cohort manipulation.

    Provides authorization capabilities in lieu of a login (something the GDC
    data portal does not and cannot implement). When a cohort is created, it
    is associated with a context ID that establishes identity similar to a
    bearer token. When a request is made to manipulate a cohort, the context ID
    must be provided as part of that request to authorize a change.

    Attributes:
        id: A unique identifier for the context.
        created_datetime: The date and time when the record is created.
        updated_datetime: The date and time when the record is updated.
    """

    __tablename__ = "anonymous_context"
    id = sqlalchemy.Column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # establishes a one-to-many relationship with Cohort
    cohorts = sqlalchemy.orm.relationship("Cohort", back_populates="context", lazy="selectin")

    def __repr__(self) -> str:
        created_datetime = self.created_datetime.isoformat() if self.created_datetime else None
        updated_datetime = self.updated_datetime.isoformat() if self.updated_datetime else None

        return (
            "<AnonymousContext("
            f"id={self.id}, "
            f"created_datetime={created_datetime}, "
            f"updated_datetime={updated_datetime})>"
        )

    def to_json(self):
        return {
            "id": str(self.id),
            "created_datetime": (
                self.created_datetime.isoformat() if self.created_datetime else None
            ),
            "updated_datetime": (
                self.updated_datetime.isoformat() if self.updated_datetime else None
            ),
        }


class Cohort(Base, audit.AuditColumnsMixin, accessed.AccessedColumnMixin):
    """A base definition for a cohort entity.

    Attributes:
        id: A unique identifier for the cohort.
        context_id: The ID of the associated context.
        name: A user defined name for the cohort.
        created_datetime: The date and time when the record is created.
        updated_datetime: The date and time when the record is last updated.
        accessed_datetime: The date and time when the record is last accessed.
    """

    __tablename__ = "cohort"
    id = sqlalchemy.Column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    context_id = sqlalchemy.Column(
        postgresql.UUID(as_uuid=True),
        sqlalchemy.ForeignKey("anonymous_context.id"),
        nullable=False,
    )

    # establishes a many-to-one relationship with AnonymousContext
    context = sqlalchemy.orm.relationship("AnonymousContext", back_populates="cohorts")

    # establishes a one-to-many relationship with CohortFilter
    filters = sqlalchemy.orm.relationship(
        "CohortFilter",
        order_by="desc(CohortFilter.id)",
        back_populates="cohort",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def get_current_filter(self):
        # type: (self) -> CohortFilter
        """Retrieves the latest filter associated with the cohort."""
        return self.filters[0]

    def __repr__(self) -> str:
        created_datetime = self.created_datetime.isoformat() if self.created_datetime else None
        updated_datetime = self.updated_datetime.isoformat() if self.updated_datetime else None
        accessed_datetime = (
            self.accessed_datetime.isoformat() if self.accessed_datetime else None
        )

        return (
            "<Cohort("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"context_id={self.context_id}, "
            f"created_datetime={created_datetime}, "
            f"updated_datetime={updated_datetime}), "
            f"accessed_datetime={accessed_datetime})>"
        )

    def to_json(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "context_id": str(self.context_id),
            "created_datetime": (
                self.created_datetime.isoformat() if self.created_datetime else None
            ),
            "updated_datetime": (
                self.updated_datetime.isoformat() if self.updated_datetime else None
            ),
            "accessed_datetime": (
                self.accessed_datetime.isoformat() if self.accessed_datetime else None
            ),
        }


class CohortFilter(Base, audit.AuditColumnsMixin):
    """A filter defining the set of cases in a cohort.

    Provides the properties for defining a cohort filter, including the filter
    itself, a cohort type indicator, and a self-referential foreign key to maintain
    a history of changes.

    Attributes:
        id: A unique identifier for the cohort.
        parent_id: A self-referential key to maintain parent-child history.
        cohort_id: The ID of the cohort associated with the filter.
        filters: A representation of the filters defining the case set
        cohort_type: A cohort type designation.
        created_datetime: The date and time when the record is created.
        updated_datetime: The date and time when the record is updated.
    """

    __tablename__ = "cohort_filter"
    id_seq = sqlalchemy.schema.Sequence(
        name="cohort_filter_id_seq",
        metadata=Base.metadata,
    )
    id = sqlalchemy.Column(
        sqlalchemy.BigInteger,
        primary_key=True,
        server_default=id_seq.next_value(),
    )
    parent_id = sqlalchemy.Column(
        sqlalchemy.BigInteger,
        sqlalchemy.ForeignKey("cohort_filter.id"),
    )
    cohort_id = sqlalchemy.Column(
        postgresql.UUID(as_uuid=True),
        sqlalchemy.ForeignKey("cohort.id"),
        nullable=False,
    )
    filters = sqlalchemy.Column(postgresql.JSONB, nullable=False)
    cohort_type = sqlalchemy.Column(sqlalchemy.Text, nullable=False, default="static")

    # establishes a many-to-one relationship with Cohort
    cohort = sqlalchemy.orm.relationship("Cohort", back_populates="filters")

    # establishes a one-to-one relationship with CohortSnapshot
    snapshot = sqlalchemy.orm.relationship(
        "CohortSnapshot",
        back_populates="filter",
        lazy="selectin",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # establishes an adjacency relationship (i.e. self-referential key)
    parent = sqlalchemy.orm.relationship("CohortFilter")

    def __repr__(self) -> str:
        created_datetime = self.created_datetime.isoformat() if self.created_datetime else None
        updated_datetime = self.updated_datetime.isoformat() if self.updated_datetime else None

        return (
            "<CohortFilter("
            f"id={self.id}, "
            f"parent_id={self.parent_id}, "
            f"cohort_id={self.cohort_id}, "
            f"filters={self.filters}, "
            f"cohort_type={self.cohort_type}, "
            f"created_datetime={created_datetime}, "
            f"updated_datetime={updated_datetime})>"
        )

    def to_json(self):
        return {
            "id": self.id,
            "parent_id": self.parent_id,
            "cohort_id": str(self.cohort_id),
            "filters": self.filters,
            "cohort_type": self.cohort_type,
            "created_datetime": (
                self.created_datetime.isoformat() if self.created_datetime else None
            ),
            "updated_datetime": (
                self.updated_datetime.isoformat() if self.updated_datetime else None
            ),
        }


class CohortSnapshot(Base, audit.AuditColumnsMixin):
    """A static snapshot of cases associated with a cohort filter.

    In the event a cohort is static, this provides a list of cases associated
    with the cohort and the data release in which they were generated.

    Attributes:
        id: A unique identifier for the snapshot.
        filter_id: The ID of the filter associated with the snapshot.
        data_release: The ID of the data release when the snapshot was created.
        case_ids: A set of case IDs.
        created_datetime: The date and time when the record is created.
        updated_datetime: The date and time when the record is updated.
    """

    __tablename__ = "cohort_snapshot"
    id_seq = sqlalchemy.schema.Sequence(
        name="cohort_snapshot_id_seq",
        metadata=Base.metadata,
    )
    id = sqlalchemy.Column(
        sqlalchemy.BigInteger,
        primary_key=True,
        server_default=id_seq.next_value(),
    )
    filter_id = sqlalchemy.Column(
        sqlalchemy.BigInteger,
        sqlalchemy.ForeignKey("cohort_filter.id"),
        nullable=False,
        unique=True,
    )
    data_release = sqlalchemy.Column(postgresql.UUID(as_uuid=True), nullable=False)
    case_ids = sqlalchemy.Column(
        postgresql.ARRAY(postgresql.UUID(as_uuid=True)),
        nullable=False,
    )

    # establishes a one-to-one relationship with CohortFilter
    filter = sqlalchemy.orm.relationship("CohortFilter", back_populates="snapshot")

    def __repr__(self) -> str:
        created_datetime = self.created_datetime.isoformat() if self.created_datetime else None
        updated_datetime = self.updated_datetime.isoformat() if self.updated_datetime else None

        return (
            "<CohortSnapshot("
            f"id={self.id}, "
            f"filter_id={self.filter_id}, "
            f"data_release={self.data_release}, "
            f"case_ids={self.case_ids}, "
            f"created_datetime={created_datetime}, "
            f"updated_datetime={updated_datetime})>"
        )

    def to_json(self):
        return {
            "id": self.id,
            "filter_id": self.filter_id,
            "data_release": str(self.data_release),
            "case_ids": [str(case_id) for case_id in self.case_ids],
            "created_datetime": (
                self.created_datetime.isoformat() if self.created_datetime else None
            ),
            "updated_datetime": (
                self.updated_datetime.isoformat() if self.updated_datetime else None
            ),
        }
