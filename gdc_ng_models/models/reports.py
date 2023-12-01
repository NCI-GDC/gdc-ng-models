from sqlalchemy import BigInteger, Column, DateTime, Index, Sequence, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()


class GDCReport(Base):
    __tablename__ = "gdc_reports"
    __table_args__ = (
        Index(f"{__tablename__}_report_idx", "report", postgresql_using="gin"),
        Index(f"{__tablename__}_report_type_idx", "report_type"),
        Index(f"{__tablename__}_created_datetime_idx", "created_datetime"),
        Index(f"{__tablename__}_program_idx", "program"),
        Index(f"{__tablename__}_project_idx", "project"),
        Index(f"{__tablename__}_id_idx", "id"),
    )

    def __repr__(self):
        return f"<Report({self.id}, {self.report_type})>"

    id_seq = Sequence("gdc_reports_id_seq", metadata=Base.metadata)
    id = Column(BigInteger, primary_key=True, server_default=id_seq.next_value())
    program = Column(Text)
    project = Column(Text)
    report = Column(JSONB)
    report_type = Column(Text, nullable=False)

    created_datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    @hybrid_property
    def project_id(self):
        return self.program + "-" + self.project

    @project_id.expression
    def project_id(cls):
        return func.concat(cls.program, "-", cls.project)
