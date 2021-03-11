import json

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.ext import declarative
from sqlalchemy.sql import schema

from gdc_ng_models.models import audit

Base = declarative.declarative_base()


class Batch(Base, audit.AuditColumnsMixin):
    """Batch class to represent a collection of nodes.

    Attributes:
        id: unique identifier for the batch
        name: name given to the batch
        project_id: project the batch is a part of
        created_datetime: the date and time when the batch is created
        updated_datetime: the date and time when the batch was last updated
    """

    __tablename__ = "batch"
    __mapper_args__ = {"eager_defaults": True}
    __table_args__ = (
        schema.PrimaryKeyConstraint("id", name="batch_pk"),
        schema.Index("batch_name_idx", "name"),
        schema.Index("batch_project_id_idx", "project_id"),
        schema.Index("batch_status_idx", "status"),
    )

    # start sequence at high number to avoid collisions with existing batch_id
    id_seq = sqlalchemy.Sequence("batch_id_seq", metadata=Base.metadata, start=1000)

    id = sqlalchemy.Column(
        sqlalchemy.BigInteger,
        nullable=False,
        server_default=id_seq.next_value(),
    )
    name = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    project_id = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    status = sqlalchemy.Column(sqlalchemy.Text, default="OPEN", nullable=False)

    members = orm.relationship(
        "BatchMembership", back_populates="batch", lazy="selectin"
    )

    @orm.validates("status")
    def validate_status(self, key, status):
        if not status:
            raise ValueError("status is required")

        status = status.upper()

        if status not in ["OPEN", "CLOSED"]:
            raise ValueError("invalid status specified")

        return status

    def __repr__(self):
        created_datetime = (
            self.created_datetime.isoformat() if self.created_datetime else None
        )
        updated_datetime = (
            self.updated_datetime.isoformat() if self.updated_datetime else None
        )

        return "<Batch(id='{}', name='{}', project_id='{}', status='{}', created_datetime='{}', updated_datetime='{}')>".format(
            self.id,
            self.name,
            self.project_id,
            self.status,
            created_datetime,
            updated_datetime,
        )

    def to_dict(self):
        created_datetime = (
            self.created_datetime.isoformat() if self.created_datetime else None
        )
        updated_datetime = (
            self.updated_datetime.isoformat() if self.updated_datetime else None
        )

        return {
            "id": self.id,
            "name": self.name,
            "project_id": self.project_id,
            "status": self.status,
            "created_datetime": created_datetime,
            "updated_datetime": updated_datetime,
        }

    def to_json(self):
        """Returns a JSON safe representation of a batch"""
        return json.loads(json.dumps(self.to_dict()))


class BatchMembership(Base, audit.AuditColumnsMixin):
    """Membership class to represent which nodes belong in a batch.

    Attributes:
        batch_id: id of the batch
        node_id: id of the node
        created_datetime: the date and time when node was added to batch
        updated_datetime: the date and time when node membership was last updated
    """

    __tablename__ = "batch_membership"
    __table_args__ = (
        schema.PrimaryKeyConstraint("batch_id", "node_id", name="batch_membership_pk"),
        schema.ForeignKeyConstraint(
            ("batch_id",),
            ("batch.id",),
            name="batch_membership_batch_id_fk",
        ),
    )

    batch_id = sqlalchemy.Column(sqlalchemy.BigInteger, nullable=False)
    node_id = sqlalchemy.Column(sqlalchemy.Text, nullable=False)

    batch = orm.relationship("Batch", back_populates="members")

    def __repr__(self):
        created_datetime = (
            self.created_datetime.isoformat() if self.created_datetime else None
        )
        updated_datetime = (
            self.updated_datetime.isoformat() if self.updated_datetime else None
        )

        return "<BatchMembership(batch_id='{}', node_id='{}', created_datetime='{}', updated_datetime='{}')>".format(
            self.batch_id,
            self.node_id,
            created_datetime,
            updated_datetime,
        )

    def to_dict(self):
        created_datetime = (
            self.created_datetime.isoformat() if self.created_datetime else None
        )
        updated_datetime = (
            self.updated_datetime.isoformat() if self.updated_datetime else None
        )

        return {
            "batch_id": self.batch_id,
            "node_id": self.node_id,
            "created_datetime": created_datetime,
            "updated_datetime": updated_datetime,
        }

    def to_json(self):
        """Returns a JSON safe representation of a membership object"""
        return json.loads(json.dumps(self.to_dict()))
