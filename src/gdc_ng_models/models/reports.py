import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext import hybrid

Base = orm.declarative_base()


class GDCReport(Base):
    __tablename__ = "gdc_reports"
    __table_args__ = (
        sqlalchemy.Index(f"{__tablename__}_report_idx", "report", postgresql_using="gin"),
        sqlalchemy.Index(f"{__tablename__}_report_type_idx", "report_type"),
        sqlalchemy.Index(f"{__tablename__}_created_datetime_idx", "created_datetime"),
        sqlalchemy.Index(f"{__tablename__}_program_idx", "program"),
        sqlalchemy.Index(f"{__tablename__}_project_idx", "project"),
        sqlalchemy.Index(f"{__tablename__}_id_idx", "id"),
    )

    def __repr__(self) -> str:
        return f"<Report({self.id}, {self.report_type})>"

    id_seq = sqlalchemy.Sequence("gdc_reports_id_seq", metadata=Base.metadata)
    id = sqlalchemy.Column(
        sqlalchemy.BigInteger, primary_key=True, server_default=id_seq.next_value()
    )
    program = sqlalchemy.Column(sqlalchemy.Text)
    project = sqlalchemy.Column(sqlalchemy.Text)
    report = sqlalchemy.Column(postgresql.JSONB)
    report_type = sqlalchemy.Column(sqlalchemy.Text, nullable=False)

    created_datetime = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        nullable=False,
        server_default=sqlalchemy.text("now()"),
    )

    @hybrid.hybrid_property
    def project_id(self):
        return self.program + "-" + self.project

    @project_id.expression
    def _project_id_expression(cls):  # noqa: N805
        return sqlalchemy.func.concat(cls.program, "-", cls.project)
