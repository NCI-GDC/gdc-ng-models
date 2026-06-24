import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.dialects import postgresql

Base = orm.declarative_base()


class FileReport(Base):
    __tablename__ = "filereport"

    id_seq = sqlalchemy.Sequence("filereport_id_seq", metadata=Base.metadata)
    id = sqlalchemy.Column(
        "id", sqlalchemy.BigInteger, primary_key=True, server_default=id_seq.next_value()
    )
    node_id = sqlalchemy.Column("node_id", sqlalchemy.Text, index=True)
    ip = sqlalchemy.Column("ip", sqlalchemy.String)
    country_code = sqlalchemy.Column("country_code", sqlalchemy.String, index=True)
    timestamp = sqlalchemy.Column("timestamp", sqlalchemy.DateTime, server_default="now()")
    streamed_bytes = sqlalchemy.Column("streamed_bytes", sqlalchemy.BigInteger)
    username = sqlalchemy.Column("username", sqlalchemy.String, index=True)
    requested_bytes = sqlalchemy.Column("requested_bytes", sqlalchemy.BigInteger)

    report_data = sqlalchemy.Column(postgresql.JSONB, nullable=True)

    __table_args__ = (
        sqlalchemy.Index(
            "filereport_report_data_idx",
            "report_data",
            postgresql_using="gin",
        ),
    )
