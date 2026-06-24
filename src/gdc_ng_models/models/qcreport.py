import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.dialects import postgresql

Base = orm.declarative_base()

SEVERITY = sqlalchemy.Enum("CRITICAL", "WARNING", "PASSED", name="error_severity")
TEST_RUN_STATUS = sqlalchemy.Enum(
    "PENDING", "RUNNING", "SUCCESS", "ERROR", "FAILED", name="test_run_status"
)


class TestRun(Base):
    __tablename__ = "qc_test_runs"

    id_seq = sqlalchemy.Sequence("qc_test_runs_id_seq", metadata=Base.metadata)
    id = sqlalchemy.Column(
        sqlalchemy.BigInteger, primary_key=True, server_default=id_seq.next_value()
    )
    project_id = sqlalchemy.Column(sqlalchemy.String(64), nullable=False, index=True)

    entity_id = sqlalchemy.Column(sqlalchemy.String(64), nullable=False)
    test_type = sqlalchemy.Column(sqlalchemy.String(64), nullable=False, index=True)
    is_stale = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)

    # e.g. pending/running/finished
    status = sqlalchemy.Column(TEST_RUN_STATUS, default="PENDING", nullable=False, index=True)

    test_results = orm.relationship(
        "ValidationResult",
        back_populates="test_run",
        cascade="all, delete, delete-orphan",
    )

    date_created = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        nullable=False,
        server_default=sqlalchemy.text("now()"),
    )

    last_updated = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        nullable=False,
        server_default=sqlalchemy.text("now()"),
    )

    def __repr__(self) -> str:
        return (
            f"<TestRun(id='{self.id}', test_type='{self.test_type}', status='{self.status}')>"
        )

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "entity_id": self.entity_id,
            "test_type": self.test_type,
            "status": self.status,
            "date_created": self.date_created.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }


class ValidationResult(Base):
    __tablename__ = "qc_validation_results"

    id_seq = sqlalchemy.Sequence("qc_validation_results_id_seq", metadata=Base.metadata)
    id = sqlalchemy.Column(
        sqlalchemy.BigInteger, primary_key=True, server_default=id_seq.next_value()
    )

    node_id = sqlalchemy.Column(sqlalchemy.String(64), nullable=False)
    submitter_id = sqlalchemy.Column(sqlalchemy.String(128), nullable=False)

    error_type = sqlalchemy.Column(
        sqlalchemy.String(128), nullable=True, default="", index=True
    )

    # from Node.label
    node_type = sqlalchemy.Column(sqlalchemy.String(128), nullable=False, index=True)
    message = sqlalchemy.Column(sqlalchemy.Text, nullable=False)

    severity = sqlalchemy.Column(SEVERITY, nullable=True, index=True)

    related_nodes = sqlalchemy.Column(postgresql.JSONB, nullable=True)

    test_run_id = sqlalchemy.Column(
        sqlalchemy.BigInteger,
        sqlalchemy.ForeignKey("qc_test_runs.id"),
        nullable=False,
        primary_key=True,
    )
    test_run = orm.relationship("TestRun", back_populates="test_results")

    date_created = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        nullable=False,
        server_default=sqlalchemy.text("now()"),
    )

    last_updated = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        nullable=False,
        server_default=sqlalchemy.text("now()"),
    )

    @orm.validates("severity")
    def validate_severity(self, key, severity):

        if not severity:
            return severity

        # ensure all upper cases
        severity = severity.upper()

        # map fatal to failed
        if severity == "FATAL":
            severity = "CRITICAL"

        return severity

    def __repr__(self) -> str:
        return f"<ValidationResult(id={self.id}, error='{self.error_type}')>"

    def to_json(self) -> dict:
        return {
            "node_id": self.node_id,
            "submitter_id": self.submitter_id,
            "error": self.error_type,
            "severity": self.severity,
            "message": self.message,
            "related_nodes": self.related_nodes,
            "date_created": self.date_created.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }
