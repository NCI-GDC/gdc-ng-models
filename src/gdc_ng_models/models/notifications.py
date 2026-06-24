import json
from collections.abc import Mapping
from typing import Any, ClassVar

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.dialects import postgresql

Base = orm.declarative_base()


class Notification(Base):
    __tablename__ = "notifications"

    id_seq = sqlalchemy.Sequence("notifications_id_seq", metadata=Base.metadata)
    id = sqlalchemy.Column(
        sqlalchemy.BigInteger, primary_key=True, server_default=id_seq.next_value()
    )
    components = sqlalchemy.Column(postgresql.ARRAY(sqlalchemy.Text), default=list())
    message = sqlalchemy.Column(sqlalchemy.String)
    level = sqlalchemy.Column(sqlalchemy.String)
    dismissible = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    created = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True),
        nullable=False,
        server_default=sqlalchemy.text("now()"),
    )
    start_date = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), nullable=True)
    end_date = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), nullable=True)

    __mapper_args__: ClassVar[Mapping[str, Any]] = {"eager_defaults": True}

    def __repr__(self) -> str:
        return (
            f"<Notification(id='{self.id}', level='{self.level}', message='{self.message}')>"
        )

    def to_dict(self) -> dict:
        """Converts the object to a dictionary.

        Returns:
            A dictionary representation of the model.
        """
        start_date = self.start_date.isoformat() if self.start_date is not None else None
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

    def to_json(self) -> dict:
        """Converts the object to a JSON safe dictionary.

        Returns:
            A dictionary w/ values which are JSON compatible.
        """
        return json.loads(json.dumps(self.to_dict()))
