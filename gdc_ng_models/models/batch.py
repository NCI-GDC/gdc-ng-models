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

    members = orm.relationship("BatchMembership", back_populates="batch")

    def __repr__(self):
        created_datetime = (
            self.created_datetime.isoformat() if self.created_datetime else None
        )
        updated_datetime = (
            self.updated_datetime.isoformat() if self.updated_datetime else None
        )

        return "<Batch(id='{}', name='{}', project_id='{}', created_datetime='{}', updated_datetime='{}')>".format(
            self.id, self.name, self.project_id, created_datetime, updated_datetime
        )

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.id == other.id
            and self.name == other.name
            and self.project_id == other.project_id
            and self.created_datetime == other.created_datetime
            and self.updated_datetime == other.updated_datetime
        )

    def __ne__(self, other):
        return not self.__eq__(other)

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
        node_type: type of the node
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
    node_type = sqlalchemy.Column(sqlalchemy.Text, nullable=False)

    batch = orm.relationship("Batch", back_populates="members")

    def __repr__(self):
        created_datetime = (
            self.created_datetime.isoformat() if self.created_datetime else None
        )
        updated_datetime = (
            self.updated_datetime.isoformat() if self.updated_datetime else None
        )

        return "<BatchMembership(batch_id='{}', node_id='{}', node_type='{}', created_datetime='{}', updated_datetime='{}')>".format(
            self.batch_id,
            self.node_id,
            self.node_type,
            created_datetime,
            updated_datetime,
        )

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.batch_id == other.batch_id
            and self.node_id == other.node_id
            and self.node_type == other.node_type
            and self.created_datetime == other.created_datetime
            and self.updated_datetime == other.updated_datetime
        )

    def __ne__(self, other):
        return not self.__eq__(other)

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
            "node_type": self.node_type,
            "created_datetime": created_datetime,
            "updated_datetime": updated_datetime,
        }

    def to_json(self):
        """Returns a JSON safe representation of a membership object"""
        return json.loads(json.dumps(self.to_dict()))