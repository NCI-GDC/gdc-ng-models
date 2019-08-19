import json
from sqlalchemy import Column, Integer, String, Text, DateTime, text, Boolean, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY


Base = declarative_base()


class Notification(Base):
    __tablename__ = 'notifications'

    id_seq = Sequence("notifications_id_seq", metadata=Base.metadata)
    id = Column(Integer, primary_key=True, server_default=id_seq.next_value())
    components = Column(ARRAY(Text), default=list())
    message = Column(String)
    level = Column(String)
    dismissible = Column(Boolean, default=True)
    created = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text('now()'),
    )

    def __repr__(self):
        return "<Notification(id='{}', level='{}', message='{}')>".format(
           self.id, self.level, self.message)

    def to_json(self):
        """Returns a JSON safe representation of :class:`Notification`"""

        return json.loads(json.dumps({
            'id': self.id,
            'components': self.components,
            'dismissible': self.dismissible,
            'message': self.message,
            'level': self.level,
        }))
