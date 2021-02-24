import json
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.ext import declarative
from sqlalchemy.sql import schema

Base = declarative.declarative_base()


class Batch(Base):
    """Batch class to represent a collection of nodes.

    Attributes:
        id: unique identifier for the batch
        name: name given to the batch
        project_id: project the batch is a part of
        created_datetime: the date and time when the batch is created
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
    project_id = sqlalchemy.Column(sqlalchemy.String(64), nullable=False)
    created_datetime = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        nullable=False,
        server_default=sqlalchemy.text("now()"),
    )

    members = orm.relationship(
        "BatchMembership",
        back_populates="batch",
        cascade="all, delete, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return "<Batch(id='{}', name='{}', project_id='{}', created_datetime='{}')>".format(
            self.id,
            self.name,
            self.project_id,
            self.created_datetime.isoformat(),
        )

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.id == other.id
            and self.name == other.name
            and self.project_id == other.project_id
            and self.created_datetime == other.created_datetime
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "project_id": self.project_id,
            "created_datetime": self.created_datetime.isoformat(),
        }

    def to_json(self):
        """Returns a JSON safe representation of a batch"""
        return json.loads(json.dumps(self.to_dict()))


class BatchMembership(Base):
    """Membership class to represent which nodes belong in a batch.

    Attributes:
        batch_id: id of the batch
        node_id: id of the node
        node_type: type of the node
    """

    __tablename__ = "batch_membership"
    __table_args__ = (
        schema.PrimaryKeyConstraint("batch_id", "node_id", name="batch_membership_pk"),
        schema.ForeignKeyConstraint(
            ("batch_id",),
            ("batch.id",),
            name="batch_membership_batch_id_fk",
            ondelete="CASCADE",
        ),
    )

    batch_id = sqlalchemy.Column(sqlalchemy.BigInteger, nullable=False)
    node_id = sqlalchemy.Column(sqlalchemy.String(64), nullable=False)
    node_type = sqlalchemy.Column(sqlalchemy.String(64), nullable=False)

    batch = orm.relationship("Batch", back_populates="members")

    def __repr__(self):
        return "<BatchMembership(batch_id='{}', node_id='{}', node_type='{}'>".format(
            self.batch_id, self.node_id, self.node_type
        )

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.batch_id == other.batch_id
            and self.node_id == other.node_id
            and self.node_type == other.node_type
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_dict(self):
        return {
            "batch_id": self.batch_id,
            "node_id": self.node_id,
            "node_type": self.node_type,
        }

    def to_json(self):
        """Returns a JSON safe representation of a membership object"""
        return json.loads(json.dumps(self.to_dict()))