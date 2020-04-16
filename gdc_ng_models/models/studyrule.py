"""Data models to describe studies.

Studies will be used for the single-study controlled-access feature in gdcapi.
These models provide a way to associate programs and projects to studies.
"""
from sqlalchemy import orm
from sqlalchemy.ext import declarative
from sqlalchemy.sql import schema, sqltypes

from gdc_ng_models.models import audit

Base = declarative.declarative_base()


class StudyRule(Base, audit.AuditColumnsMixin):
    """A study rule for use with single-study controlled-access.

    Attributes:
        id: A unique identifier for the study rule.
        name: A unique, informational name for the study rule.
        created_date: The date and time when the record is created.
        updated_date: The date and time when the record is updated.
    """

    __tablename__ = "study_rule"
    id_seq = schema.Sequence(name="study_rule_id_seq", metadata=Base.metadata)
    id = schema.Column(sqltypes.Integer, nullable=False, server_default=id_seq.next_value())
    name = schema.Column(sqltypes.Text, nullable=False)

    __table_args__ = (
        schema.PrimaryKeyConstraint("id", name="study_rule_pk"),
        schema.Index("study_rule_name_idx", "name", unique=True),
    )

    whole_programs = orm.relationship("StudyRuleProgram", lazy="joined")
    partial_programs = orm.relationship("StudyRuleProgramProject", lazy="joined")

    def __repr__(self):
        return "<StudyRule(id={id}, name='{name}', created_date={created_date}, updated_date={updated_date})>".format(
            id=self.id,
            name=self.name,
            created_date=self.created_date.isoformat(),
            updated_date=self.updated_date.isoformat(),
        )

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_date": self.created_date.isoformat(),
            "updated_date": self.updated_date.isoformat(),
        }


class StudyRuleProgram(Base, audit.AuditColumnsMixin):
    """A relationship between study rules and programs.

    A study rule can contain one or more programs. This relationship is used when the
    study rule includes all projects in the program.

    Attributes:
        study_rule_id: The id of the associated study rule.
        program_name: The name of the program to associate with the study rule.
        created_date: The date and time when the record is created.
        updated_date: The date and time when the record is updated.
    """

    __tablename__ = "study_rule_program"
    study_rule_id = schema.Column(sqltypes.Integer, nullable=False)
    program_name = schema.Column(sqltypes.Text, nullable=False)

    __table_args__ = (
        schema.PrimaryKeyConstraint("study_rule_id", "program_name", name="study_rule_program_pk"),
        schema.ForeignKeyConstraint(("study_rule_id",), ("study_rule.id",), name="study_rule_program_study_rule_id_fk")
    )

    def __repr__(self):
        return "<StudyRuleProgram(study_rule_id={study_rule_id}, program_name='{program_name}', created_date={created_date}, updated_date={updated_date})>".format(
            study_rule_id=self.study_rule_id,
            program_name=self.program_name,
            created_date=self.created_date.isoformat(),
            updated_date=self.updated_date.isoformat(),
        )

    def to_json(self):
        return {
            "study_rule_id": self.study_rule_id,
            "program_name": self.program_name,
            "created_date": self.created_date.isoformat(),
            "updated_date": self.updated_date.isoformat(),
        }


class StudyRuleProgramProject(Base, audit.AuditColumnsMixin):
    """A relationship between study rules, programs, and projects.

    A study rule can contain one or more programs. For each program, one or more projects
    can be associated.

    This relationship is used when the study rule includes a subset of projects from a
    program.

    Attributes:
        study_rule_id: The id of the associated study rule.
        program_name: The name of the program to associate with the study rule.
        project_code: The code of the project to associate with the study rule.
        created_date: The date and time when the record is created.
        updated_date: The date and time when the record is updated.
    """

    __tablename__ = "study_rule_program_project"
    study_rule_id = schema.Column(sqltypes.Integer, nullable=False)
    program_name = schema.Column(sqltypes.Text, nullable=False)
    project_code = schema.Column(sqltypes.Text, nullable=False)

    __table_args__ = (
        schema.PrimaryKeyConstraint("study_rule_id", "program_name", "project_code", name="study_rule_program_project_pk"),
        schema.ForeignKeyConstraint(("study_rule_id",), ("study_rule.id",), name="study_rule_program_project_study_rule_id_fk"),
    )

    def __repr__(self):
        return "<StudyRuleProgramProject(study_rule_id={study_rule_id}, program_name='{program_name}', project_code='{project_code}', created_date={created_date}, updated_date={updated_date})>".format(
            study_rule_id=self.study_rule_id,
            program_name=self.program_name,
            project_code=self.project_code,
            created_date=self.created_date.isoformat(),
            updated_date=self.updated_date.isoformat(),
        )

    def to_json(self):
        return {
            "study_rule_id": self.study_rule_id,
            "program_name": self.program_name,
            "project_code": self.project_code,
            "created_date": self.created_date.isoformat(),
            "updated_date": self.updated_date.isoformat(),
        }
