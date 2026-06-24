"""Models for submission TransactionLogs."""

import json
from datetime import datetime

import pytz
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext import declarative, hybrid

Base = orm.declarative_base()


def datetime_to_unix(dt):
    return (dt - datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds()


class TransactionLog(Base):
    __tablename__ = "transaction_logs"

    @declarative.declared_attr
    def __table_args__(cls):  # noqa: N805
        tbl = cls.__tablename__

        return (
            sqlalchemy.Index(f"{tbl}_program_idx", "program"),
            sqlalchemy.Index(f"{tbl}_project_idx", "project"),
            sqlalchemy.Index(f"{tbl}_is_dry_run_idx", "is_dry_run"),
            sqlalchemy.Index(f"{tbl}_committed_by_idx", "committed_by"),
            sqlalchemy.Index(f"{tbl}_closed_idx", "closed"),
            sqlalchemy.Index(f"{tbl}_state_idx", "state"),
            sqlalchemy.Index(f"{tbl}_submitter_idx", "submitter"),
            sqlalchemy.Index(f"{tbl}_created_datetime_idx", "created_datetime"),
            sqlalchemy.Index(f"{tbl}_project_id_idx", cls.program + "-" + cls.project),
        )

    def __repr__(self) -> str:
        return f"<TransactionLog({self.id}, {self.created_datetime})>"

    def to_json(self, fields=None):

        fields = fields or set()
        # Source fields
        existing_fields = [c.name for c in self.__table__.c] + ["entities", "documents"]
        custom_fields = {"created_datetime", "entities", "documents"}

        # Pull out child fields
        entity_fields = {f for f in fields if f.startswith("entities.")}
        document_fields = {f for f in fields if f.startswith("documents.")}
        fields = fields - entity_fields - document_fields

        # Reformat child fields
        entity_fields = {f.replace("entities.", "") for f in entity_fields}
        document_fields = {f.replace("documents.", "") for f in document_fields}

        # Default fields
        if not fields:
            fields = {"id", "submitter", "role", "program", "created_datetime"}

        # Check for field existence
        if set(fields) - set(existing_fields):
            raise RuntimeError(
                "Fields do not exist: {}".format(", ".join(set(fields) - set(existing_fields)))
            )

        # Set standard fields
        doc = {key: getattr(self, key) for key in fields if key not in custom_fields}

        # Add custom fields
        if "entities" in fields or entity_fields:
            doc["entities"] = [n.to_json(entity_fields) for n in self.entities]
        if "documents" in fields or document_fields:
            doc["documents"] = [n.to_json(document_fields) for n in self.documents]
        if "created_datetime" in fields:
            doc["created_datetime"] = self.created_datetime.isoformat("T")

        return doc

    id_seq = sqlalchemy.Sequence("transaction_logs_id_seq", metadata=Base.metadata)
    id = sqlalchemy.Column(
        sqlalchemy.BigInteger, primary_key=True, server_default=id_seq.next_value()
    )

    submitter = sqlalchemy.Column(
        sqlalchemy.Text,
    )

    role = sqlalchemy.Column(
        sqlalchemy.Text,
        nullable=False,
    )

    program = sqlalchemy.Column(
        sqlalchemy.Text,
        nullable=False,
    )

    project = sqlalchemy.Column(
        sqlalchemy.Text,
        nullable=False,
    )

    #: Specifies a non-dry_run transaction that repeated this
    #: transaction in an attempt to write to the database
    committed_by = sqlalchemy.Column(
        sqlalchemy.Integer,
    )

    #: Was this transaction a dry_run (for validation)
    is_dry_run = sqlalchemy.Column(
        sqlalchemy.Boolean,
        nullable=False,
    )

    #: Has this transaction succeeded, errored, failed, etc.
    state = sqlalchemy.Column(
        sqlalchemy.Text,
        nullable=False,
    )

    closed = sqlalchemy.Column(
        sqlalchemy.Boolean,
        default=False,
        nullable=False,
    )

    @hybrid.hybrid_property
    def project_id(self):
        return self.program + "-" + self.project

    @project_id.comparator
    def _project_id_comparator(cls):  # noqa: N805
        return sqlalchemy.func.concat(cls.program, "-", cls.project)

    created_datetime = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        nullable=False,
        server_default=sqlalchemy.text("now()"),
    )

    canonical_json = orm.deferred(
        sqlalchemy.Column(
            postgresql.JSONB,
            server_default="[]",
            nullable=False,
        )
    )


class TransactionSnapshot(Base):
    __tablename__ = "transaction_snapshots"
    __table_args__ = (
        sqlalchemy.Index("idx_transaction_snapshots_transactions_id", "transaction_id"),
    )

    def __repr__(self) -> str:
        return f"<TransactionSnapshot({self.id}, {self.transaction_id})>"

    def to_json(self, fields=None):
        fields = set(fields) if fields else set()
        existing_fields = [c.name for c in self.__table__.c]
        if not fields:
            fields = existing_fields
        if set(fields) - set(existing_fields):
            raise RuntimeError(
                "Entity fields do not exist: {}".format(
                    ", ".join(set(fields) - set(existing_fields))
                )
            )
        doc = {key: getattr(self, key) for key in fields}
        return doc

    id = sqlalchemy.Column(
        sqlalchemy.Text,
        primary_key=True,
        nullable=False,
    )

    transaction_id = sqlalchemy.Column(
        sqlalchemy.BigInteger,
        sqlalchemy.ForeignKey("transaction_logs.id"),
        primary_key=True,
    )

    action = sqlalchemy.Column(
        sqlalchemy.Text,
        nullable=False,
    )

    old_props = sqlalchemy.Column(
        postgresql.JSONB,
        nullable=False,
    )

    new_props = sqlalchemy.Column(
        postgresql.JSONB,
        nullable=False,
    )

    transaction = orm.relationship("TransactionLog", backref="entities")


class TransactionDocument(Base):
    __tablename__ = "transaction_documents"
    __table_args__ = (
        sqlalchemy.Index("idx_transaction_document_transactions_id", "transaction_id"),
    )

    def to_json(self, fields=None):
        # Source fields
        fields = set(fields) if fields else set()
        existing_fields = {c.name for c in self.__table__.c}

        # Default fields
        if not fields:
            fields = existing_fields

        # Check field existence
        if set(fields) - set(existing_fields):
            raise RuntimeError(
                "Entity fields do not exist: {}".format(", ".join(fields - existing_fields))
            )

        # Generate doc
        doc = {key: getattr(self, key) for key in fields}
        return doc

    id_seq = sqlalchemy.Sequence("transaction_documents_id_seq", metadata=Base.metadata)
    id = sqlalchemy.Column(
        sqlalchemy.BigInteger,
        primary_key=True,
        nullable=False,
        server_default=id_seq.next_value(),
    )

    transaction_id = sqlalchemy.Column(
        sqlalchemy.BigInteger,
        sqlalchemy.ForeignKey("transaction_logs.id"),
        primary_key=True,
    )

    name = sqlalchemy.Column(
        sqlalchemy.Text,
    )

    doc_format = sqlalchemy.Column(
        sqlalchemy.Text,
        nullable=False,
    )

    doc = orm.deferred(
        sqlalchemy.Column(
            sqlalchemy.Text,
            nullable=False,
        )
    )

    response_json = orm.deferred(
        sqlalchemy.Column(
            postgresql.JSONB,
        )
    )

    transaction = orm.relationship("TransactionLog", backref="documents")

    @property
    def is_json(self):
        if self.doc_format.upper() != "JSON":
            return False
        else:
            return True

    @property
    def is_xml(self):
        if self.doc_format.upper() != "XML":
            return False
        else:
            return True

    @property
    def json(self):
        if not self.is_json:
            return None
        return json.loads(self.doc)

    @json.setter
    def json(self, doc):
        self.doc_format = "JSON"
        self.doc = json.dumps(doc)

    @property
    def xml(self):
        if not self.is_xml:
            return None
        return self.doc

    @xml.setter
    def xml(self, doc):
        self.doc_format = "XML"
        self.doc = doc
