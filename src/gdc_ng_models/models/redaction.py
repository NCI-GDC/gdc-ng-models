from datetime import datetime

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.ext import hybrid

Base = orm.declarative_base()


class RedactionLog(Base):
    """Logs a redaction event, each redacted node will be stored as a RedactionEntry."""

    __tablename__ = "redaction_log"

    id_seq = sqlalchemy.Sequence("redaction_log_id_seq", metadata=Base.metadata)
    id = sqlalchemy.Column(
        sqlalchemy.BigInteger, primary_key=True, server_default=id_seq.next_value()
    )
    annotation_id = sqlalchemy.Column(sqlalchemy.String(64), nullable=False, unique=True)

    # who initiated the redaction
    initiated_by = sqlalchemy.Column(sqlalchemy.String(64), nullable=False, index=True)

    # who rescinded this redaction
    rescinded_by = sqlalchemy.Column(sqlalchemy.String(64), nullable=True)

    # reasons for redaction
    reason = sqlalchemy.Column(sqlalchemy.Text, nullable=False)  # long sqlalchemy.text
    reason_category = sqlalchemy.Column(
        sqlalchemy.String(128), nullable=False, index=True
    )  # short desc

    project_id = sqlalchemy.Column(sqlalchemy.String(32), nullable=False, index=True)

    # LATEST => only latest version is redacted
    # COMPLETE => all versions are redacted
    # PREVIOUS => All previous versions are redacted
    # applicable only to files on indexd
    redaction_type = sqlalchemy.Column(
        sqlalchemy.Enum("LATEST", "COMPLETE", "PREVIOUS", name="redaction_types"),
        default="COMPLETE",
    )

    created_datetime = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        nullable=False,
        server_default=sqlalchemy.text("now()"),
    )

    date_rescinded = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), nullable=True)

    entries = orm.relationship("RedactionEntry", back_populates="redaction_log")  # type: list[RedactionEntry]

    @hybrid.hybrid_property
    def project(self):
        return "-".join(self.project_id.split("-")[1:])

    @hybrid.hybrid_property
    def program(self):
        return self.project_id.split("-")[0]

    def rescind_all(self, rescinded_by):
        """Rescinds all entries on this redaction log."""
        self.rescinded_by = rescinded_by
        self.date_rescinded = datetime.now()
        for entry in self.entries:
            entry.rescind(rescinded_by)

    @hybrid.hybrid_property
    def is_rescinded(self) -> bool:
        """Checks if all redacted entries in this log has been rescinded.

        Returns:
           True if all entries are rescinded; otherwise, false is returned.
        """
        for entry in self.entries:
            if not entry.rescinded:
                return False
        return True

    def to_json(self) -> dict:
        json = dict(
            id=self.id,
            annotation_id=self.annotation_id,
            project_id=self.project_id,
            initiated_by=self.initiated_by,
            reason=self.reason,
        )
        return json


class RedactionEntry(Base):
    """Logs a redacted node w/ enough information to query and filter redacted nodes."""

    __tablename__ = "redaction_entry"

    node_id = sqlalchemy.Column(sqlalchemy.String(64), nullable=False, primary_key=True)
    version = sqlalchemy.Column(sqlalchemy.String(4), index=True)
    file_name = sqlalchemy.Column(sqlalchemy.String(256))
    node_type = sqlalchemy.Column(sqlalchemy.String(128), nullable=False, index=True)
    release_number = sqlalchemy.Column(sqlalchemy.String(16), index=True)

    redaction_id = sqlalchemy.Column(
        sqlalchemy.BigInteger,
        sqlalchemy.ForeignKey("redaction_log.id"),
        nullable=False,
        primary_key=True,
    )
    redaction_log = orm.relationship("RedactionLog", back_populates="entries")

    rescinded = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    # who rescinded this redaction
    rescinded_by = sqlalchemy.Column(sqlalchemy.String(64), nullable=True)

    created_datetime = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        nullable=False,
        server_default=sqlalchemy.text("now()"),
    )

    date_rescinded = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), nullable=True)

    def rescind(self, rescinded_by):
        """Performs a rescind action on an entry."""
        self.rescinded = True
        self.rescinded_by = rescinded_by
        self.date_rescinded = datetime.now()

    @hybrid.hybrid_property
    def is_indexed(self):
        return self.file_name is not None

    def to_json(self) -> dict:
        return dict(
            node_id=self.node_id,
            redaction_id=self.redaction_id,
            is_indexed=self.is_indexed,
            node_type=self.node_type,
            rescinded=self.rescinded,
        )
