from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    Sequence)
from sqlalchemy.dialects.postgresql import JSONB


Base = declarative_base()


class FileReport(Base):
    __tablename__ = 'filereport'

    id = Column('id', BigInteger, primary_key=True, autoincrement=True)
    node_id = Column('node_id', Text, index=True)
    ip = Column('ip', String)
    country_code = Column('country_code', String, index=True)
    timestamp = Column('timestamp', DateTime, server_default="now()")
    streamed_bytes = Column('streamed_bytes', BigInteger)
    username = Column('username', String, index=True)
    requested_bytes = Column('requested_bytes', BigInteger)

    report_data = Column(JSONB, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint("id","timestamp"),
        Index("filereport_report_data_idx", "report_data", postgresql_using="gin",),
        Index("timestamp_idx", "timestamp", postgresql_using="btree",),
        {'postgresql_partition_by': 'RANGE (timestamp)'}
    )
