from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates
from sqlalchemy.sql import schema, sqltypes

from gdc_ng_models.models import audit

Base = declarative_base()


RELEASE_DATA_TYPE_VALUES = ["ssm", "cnv", "case"]


class ReleasedDataMixin:
    program_name = schema.Column(sqltypes.Text, nullable=False)
    project_code = schema.Column(sqltypes.Text, nullable=False)
    is_open = schema.Column(sqltypes.Boolean, nullable=False)
    data_type = schema.Column(sqltypes.Text, nullable=False)

    @property
    def project_id(self):
        return "{}-{}".format(self.program_name, self.project_code)

    @validates("data_type")
    def validate_data_type(self, key, data_type):
        assert data_type in RELEASE_DATA_TYPE_VALUES
        return data_type


class ReleasedData(Base, audit.AuditColumnsMixin, ReleasedDataMixin):

    __tablename__ = "released_data"
    __table_args__ = (
        schema.Index("released_data_project_id_idx", "program_name", "project_code"),
        schema.PrimaryKeyConstraint(
            "program_name",
            "project_code",
            "data_type",
            name="released_data_program_project_data_type_pk",
        ),
    )

    def __repr__(self):
        return "<ReleasedData(project_id='{}', data_type='{}', is_controlled={}, is_open={})>".format(
            self.project_id, self.data_type, self.is_controlled, self.is_open,
        )

    is_controlled = schema.Column(sqltypes.Boolean, nullable=False)

    def to_json(self):
        return {
            "program_name": self.program_name,
            "project_code": self.project_code,
            "data_type": self.data_type,
            "is_controlled": self.is_controlled,
            "is_open": self.is_open,
        }


class ReleasedDataLog(Base, audit.AuditColumnsMixin, ReleasedDataMixin):

    __tablename__ = "released_log"
    __table_args__ = (
        schema.Index("released_log_data_project_id_idx", "program_name", "project_code"),
        schema.PrimaryKeyConstraint("id", name="released_log_id_pk"),
    )

    def __repr__(self):
        return "<ReleasedDataLog(project_id='{}', release_number={}, data_type='{}', is_open={})>".format(
            self.project_id, self.release_number, self.data_type, self.is_open,
        )

    release_data_log_id_seq = schema.Sequence(
        name="release_data_log_id_seq", metadata=Base.metadata
    )
    id = schema.Column(
        sqltypes.Integer,
        primary_key=True,
        nullable=False,
        server_default=release_data_log_id_seq.next_value(),
    )
    release_number = schema.Column(sqltypes.Text, nullable=False)

    def to_json(self):
        return {
            "program_name": self.program_name,
            "project_code": self.project_code,
            "release_number": self.release_number,
            "data_type": self.data_type,
            "is_open": self.is_open,
        }
