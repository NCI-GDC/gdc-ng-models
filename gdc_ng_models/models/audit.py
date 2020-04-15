"""Common audit metadata for our data models."""

from sqlalchemy import schema
from sqlalchemy.sql import sqltypes


class AuditColumnsMixin:
    """A mixin to add audit columns to a data model.

    Attributes:
        created_date: Metadata describing when a row was created.
        updated_date: Metadata describing when a row was last updated.
    """

    def __init__(self):
        pass

    created_date = schema.Column(sqltypes.DateTime(timezone=True), nullable=False, server_default='now()')
    updated_date = schema.Column(sqltypes.DateTime(timezone=True), nullable=False, server_default='now()')
