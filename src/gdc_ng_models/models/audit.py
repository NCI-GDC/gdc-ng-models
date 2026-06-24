"""Common audit metadata for our data models."""

import datetime

from sqlalchemy import schema, sql
from sqlalchemy.sql import sqltypes


class AuditColumnsMixin:
    """A mixin to add audit columns to a data model.

    Attributes:
        created_datetime: Metadata describing when a row was created.
        updated_datetime: Metadata describing when a row was last updated.
    """

    created_datetime = schema.Column(
        sqltypes.DateTime(timezone=True),
        nullable=False,
        server_default=sql.text("now()"),
    )
    updated_datetime = schema.Column(
        sqltypes.DateTime(timezone=True),
        nullable=False,
        server_default=sql.text("now()"),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
    )
