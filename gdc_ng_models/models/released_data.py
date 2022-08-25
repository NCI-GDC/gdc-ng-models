from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates
from sqlalchemy.sql import schema, sqltypes

from gdc_ng_models.models import audit

Base = declarative_base()

RELEASED_DATA_DATA_TYPE_VALUES = frozenset({"ssm", "cnv", "case"})
RELEASED_DATA_LOG_ACTION_VALUES = frozenset({"release", "unrelease"})


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
        if data_type not in RELEASED_DATA_DATA_TYPE_VALUES:
            raise ValueError(
                """"{data_type}" is not a valid value for {key}""".format(
                    data_type=data_type, key=key
                )
            )
        return data_type


class ReleasedData(Base, audit.AuditColumnsMixin, ReleasedDataMixin):
    __tablename__ = "released_data"
    __table_args__ = (
        schema.PrimaryKeyConstraint(
            "program_name",
            "project_code",
            "data_type",
            name="released_data_pk",
        ),
    )

    def __repr__(self):
        return "<ReleasedData(project_id='{}', data_type='{}', is_controlled={}, is_open={})>".format(
            self.project_id,
            self.data_type,
            self.is_controlled,
            self.is_open,
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

    @hybrid_property
    def id(self):
        return "{}_{}_{}".format(self.program_name, self.project_code, self.data_type)


class ReleasedDataLog(Base, audit.AuditColumnsMixin, ReleasedDataMixin):
    __tablename__ = "released_data_log"
    __table_args__ = (
        schema.Index(
            "released_data_log_program_name_project_code_idx",
            "program_name",
            "project_code",
        ),
        schema.PrimaryKeyConstraint("id", name="released_data_log_pk"),
    )

    def __repr__(self):
        return "<ReleasedDataLog(project_id='{}', release_number={}, data_type='{}', is_open={}, action='{}')>".format(
            self.project_id,
            self.release_number,
            self.data_type,
            self.is_open,
            self.action,
        )

    release_data_log_id_seq = schema.Sequence(
        name="release_data_log_id_seq", metadata=Base.metadata
    )
    id = schema.Column(
        sqltypes.BigInteger,
        nullable=False,
        server_default=release_data_log_id_seq.next_value(),
    )
    release_number = schema.Column(sqltypes.Text, nullable=False)
    action = schema.Column(sqltypes.Text, nullable=False)

    @validates("action")
    def validate_action(self, key, action):
        if action not in RELEASED_DATA_LOG_ACTION_VALUES:
            raise ValueError(
                """"{action}" is not a valid value for {key}""".format(
                    action=action, key=key
                )
            )
        return action

    def to_json(self):
        return {
            "program_name": self.program_name,
            "project_code": self.project_code,
            "release_number": self.release_number,
            "data_type": self.data_type,
            "is_open": self.is_open,
            "action": self.action,
        }
