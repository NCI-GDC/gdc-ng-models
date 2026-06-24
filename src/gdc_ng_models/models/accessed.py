"""Mixin for adding an accessed timestamp to track the last time a record was accessed."""

import datetime

from sqlalchemy import schema, sql
from sqlalchemy.sql import sqltypes


class AccessedColumnMixin:
    """A mixin to add accessed timestamp column to a data model.

    Attributes:
        accessed_datetime: Metadata describing when a row was last accessed.
    """

    accessed_datetime = schema.Column(
        sqltypes.DateTime(timezone=True),
        nullable=False,
        server_default=sql.text("now()"),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
    )
