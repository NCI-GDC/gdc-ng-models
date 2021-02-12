from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Index,
    String,
    Text,
    Sequence,
    func)
from sqlalchemy.dialects.postgresql import JSONB


Base = declarative_base()


class FileReport(Base):
    __tablename__ = 'filereport'

    id_seq = Sequence("filereport_id_seq", metadata=Base.metadata)
    id = Column('id', BigInteger, primary_key=True, server_default=id_seq.next_value())
    node_id = Column('node_id', Text, index=True)
    ip = Column('ip', String)
    country_code = Column('country_code', String, index=True)
    timestamp = Column('timestamp', DateTime, server_default=func.now(), primary_key=True)
    streamed_bytes = Column('streamed_bytes', BigInteger)
    username = Column('username', String, index=True)
    requested_bytes = Column('requested_bytes', BigInteger)

    report_data = Column(JSONB, nullable=True)

    __table_args__ = (
        Index("filereport_report_data_idx", "report_data", postgresql_using="gin",),
        {'postgresql_partition_by': 'RANGE (timestamp)'}
    )
