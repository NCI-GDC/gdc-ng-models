import json

from sqlalchemy import BigInteger, Column, String, Text, DateTime, text, Boolean, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY


Base = declarative_base()


class Notification(Base):
    __tablename__ = "notifications"

    id_seq = Sequence("notifications_id_seq", metadata=Base.metadata)
    id = Column(BigInteger, primary_key=True, server_default=id_seq.next_value())
    components = Column(ARRAY(Text), default=list())
    message = Column(String)
    level = Column(String)
    dismissible = Column(Boolean, default=True)
    created = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)

    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return "<Notification(id='{}', level='{}', message='{}')>".format(
            self.id, self.level, self.message
        )

    def to_dict(self):
        """Returns a dictionary representation of :class:`Notification`"""
        start_date = (
            self.start_date.isoformat() if self.start_date is not None else None
        )
        end_date = self.end_date.isoformat() if self.end_date is not None else None

        return {
            "id": self.id,
            "components": self.components,
            "created": self.created.isoformat(),
            "dismissible": self.dismissible,
            "message": self.message,
            "level": self.level,
            "start_date": start_date,
            "end_date": end_date,
        }

    def to_json(self):
        """Returns a JSON safe representation of :class:`Notification`"""
        return json.loads(json.dumps(self.to_dict()))
