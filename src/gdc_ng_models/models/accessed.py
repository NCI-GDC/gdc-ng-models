"""A module for tracking when a record was last accessed."""

import datetime

from sqlalchemy import schema, sql
from sqlalchemy.sql import sqltypes


class AccessedColumnMixin:
    """A mixin to add accessed timestamp column to a data model.

    Attributes:
        accessed_datetime: Metadata describing when a row was last accessed.
    """

    def __init__(self):
        pass

    accessed_datetime = schema.Column(
        sqltypes.DateTime(timezone=True),
        nullable=False,
        server_default=sql.text("now()"),
        onupdate=datetime.datetime.now(datetime.timezone.utc),
    )
