import datetime
import json

import pytest
import pytz
from sqlalchemy import exc

from gdc_ng_models.models import studyrule


def test_study_rule__defaults_unique_ids(create_study_rule_db, db_session):
    db_session.add(studyrule.StudyRule(name="first"))
    db_session.add(studyrule.StudyRule(name="second"))
    db_session.commit()

    first = db_session.query(studyrule.StudyRule).filter(studyrule.StudyRule.name == "first").one()
    second = db_session.query(studyrule.StudyRule).filter(studyrule.StudyRule.name == "second").one()
    assert first.id is not None
    assert second.id is not None
    assert first.id != second.id


def test_study_rule__unique_id(create_study_rule_db, db_session):
    db_session.add(studyrule.StudyRule(id=1618, name="first"))
    db_session.commit()

    with pytest.raises(exc.IntegrityError, match=r"study_rule_pk"):
        db_session.add(studyrule.StudyRule(id=1618, name="second"))
        db_session.commit()


def test_study_rule__name_must_be_defined(create_study_rule_db, db_session):
    with pytest.raises(exc.IntegrityError, match=r"violates not-null constraint"):
        db_session.add(studyrule.StudyRule(id=1618))
        db_session.commit()


def test_study_rule__unique_name(create_study_rule_db, db_session):
    db_session.add(studyrule.StudyRule(name="dupe"))
    db_session.commit()

    with pytest.raises(exc.IntegrityError, match=r"study_rule_name_idx"):
        db_session.add(studyrule.StudyRule(name="dupe"))
        db_session.commit()


def test_study_rule__defaults_created_datetime(create_study_rule_db, db_session):
    db_session.add(studyrule.StudyRule(name="asdf"))
    db_session.commit()
    s = db_session.query(studyrule.StudyRule).filter(studyrule.StudyRule.name == "asdf").one()
    assert s.created_datetime is not None


def test_study_rule__defaults_updated_datetime(create_study_rule_db, db_session):
    db_session.add(studyrule.StudyRule(name="asdf"))
    db_session.commit()
    s = db_session.query(studyrule.StudyRule).filter(studyrule.StudyRule.name == "asdf").one()
    assert s.updated_datetime is not None


def test_study_rule__updates_updated_datetime(create_study_rule_db, db_session):
    db_session.add(studyrule.StudyRule(id=1618, name="asdf"))
    db_session.commit()

    db_session.query(studyrule.StudyRule).filter(studyrule.StudyRule.id == 1618).update({"name": "updated"})
    db_session.commit()

    updated = db_session.query(studyrule.StudyRule).filter(studyrule.StudyRule.id == 1618).one()
    assert updated.updated_datetime > updated.created_datetime


def test_study_rule__whole_programs(create_study_rule_db, db_session):
    """Test that study.whole_programs populate correctly.

    Each study should contain it's corresponding records from
    StudyRuleProgram.
    """
    db_session.add(studyrule.StudyRule(id=1618, name="first"))
    db_session.add(studyrule.StudyRule(id=3141, name="second"))
    db_session.commit()

    db_session.add(studyrule.StudyRuleProgram(study_rule_id=1618, program_name="alpha"))
    db_session.add(studyrule.StudyRuleProgram(study_rule_id=1618, program_name="beta"))
    db_session.commit()

    first_study = db_session.query(studyrule.StudyRule).filter(studyrule.StudyRule.id == 1618).one()
    assert len(first_study.whole_programs) == 2
    assert all([program.study_rule_id == 1618 for program in first_study.whole_programs])

    second_study = db_session.query(studyrule.StudyRule).filter(studyrule.StudyRule.id == 3141).one()
    assert len(second_study.whole_programs) == 0


def test_study_rule__partial_programs(create_study_rule_db, db_session):
    """Test that study.partial_programs populate correctly.

    Each study should contain it's corresponding records from
    StudyRuleProgramProject.
    """
    db_session.add(studyrule.StudyRule(id=1618, name="first"))
    db_session.add(studyrule.StudyRule(id=3141, name="second"))
    db_session.commit()

    db_session.add(studyrule.StudyRuleProgramProject(study_rule_id=1618, program_name="alpha", project_code="uno"))
    db_session.add(studyrule.StudyRuleProgramProject(study_rule_id=1618, program_name="alpha", project_code="dos"))
    db_session.commit()

    first_study = db_session.query(studyrule.StudyRule).filter(studyrule.StudyRule.id == 1618).one()
    assert len(first_study.partial_programs) == 2
    assert all([program.study_rule_id == 1618 for program in first_study.partial_programs])

    second_study = db_session.query(studyrule.StudyRule).filter(studyrule.StudyRule.id == 3141).one()
    assert len(second_study.partial_programs) == 0


def test_study_rule__to_json():
    s = studyrule.StudyRule(
        id=1618,
        name="asdf",
        created_datetime=datetime.datetime(
            year=2020,
            month=4,
            day=15,
            hour=12,
            minute=45,
            second=21,
            microsecond=123,
            tzinfo=pytz.utc,
        ),
        updated_datetime=datetime.datetime(
            year=2020,
            month=4,
            day=16,
            hour=12,
            minute=45,
            second=21,
            microsecond=123,
            tzinfo=pytz.utc,
        ))
    expected = json.loads(json.dumps({
        "id": 1618,
        "name": "asdf",
        "created_datetime": "2020-04-15T12:45:21.000123+00:00",
        "updated_datetime": "2020-04-16T12:45:21.000123+00:00",
    }))
    assert s.to_json() == expected


def test_study_rule__to_json_without_dates():
    s = studyrule.StudyRule(
        id=1618,
        name="asdf",
    )
    expected = json.loads(json.dumps({
        "id": 1618,
        "name": "asdf",
        "created_datetime": None,
        "updated_datetime": None,
    }))
    assert s.to_json() == expected


def test_study_rule__str():
    s = studyrule.StudyRule(
        id=1618,
        name="asdf",
        created_datetime=datetime.datetime(
            year=2020,
            month=4,
            day=15,
            hour=12,
            minute=45,
            second=21,
            microsecond=123,
            tzinfo=pytz.utc,
        ),
        updated_datetime=datetime.datetime(
            year=2020,
            month=4,
            day=16,
            hour=12,
            minute=45,
            second=21,
            microsecond=123,
            tzinfo=pytz.utc,
        ))
    expected = "<StudyRule(id=1618, name='asdf', created_datetime=2020-04-15T12:45:21.000123+00:00, updated_datetime=2020-04-16T12:45:21.000123+00:00)>"
    assert str(s) == expected


def test_study_rule__str_without_date():
    s = studyrule.StudyRule(
        id=1618,
        name="asdf",
    )
    expected = "<StudyRule(id=1618, name='asdf', created_datetime=None, updated_datetime=None)>"
    assert str(s) == expected


def test_study_rule_program__study_rule_must_exist(create_study_rule_db, db_session):
    with pytest.raises(exc.IntegrityError, match=r"study_rule_program_study_rule_id_fk"):
        db_session.add(studyrule.StudyRuleProgram(study_rule_id=1618, program_name="game_of_life"))
        db_session.commit()


@pytest.mark.filterwarnings(
    "ignore:Column 'study_rule_program.study_rule_id' is marked as a member of the primary key for table 'study_rule_program'")
def test_study_rule_program__study_rule_id_must_be_defined(create_study_rule_db, db_session):
    with pytest.raises(exc.IntegrityError, match=r"violates not-null constraint"):
        db_session.add(studyrule.StudyRuleProgram(program_name="game_of_life"))
        db_session.commit()


@pytest.mark.filterwarnings(
    "ignore:Column 'study_rule_program.program_name' is marked as a member of the primary key for table 'study_rule_program'")
def test_study_rule_program__program_name_must_be_defined(create_study_rule_db, db_session):
    with pytest.raises(exc.IntegrityError, match=r"violates not-null constraint"):
        db_session.add(studyrule.StudyRuleProgram(study_rule_id=1618))
        db_session.commit()


def test_study_rule_program__study_rule_can_contain_multiple_programs(create_study_rule_db, db_session):
    db_session.add(studyrule.StudyRule(id=1618, name="asdf"))
    db_session.commit()

    db_session.add(studyrule.StudyRuleProgram(study_rule_id=1618, program_name="alpha"))
    db_session.add(studyrule.StudyRuleProgram(study_rule_id=1618, program_name="beta"))
    db_session.commit()

    assert db_session.query(studyrule.StudyRuleProgram).filter(
        studyrule.StudyRuleProgram.study_rule_id == 1618).count() == 2


def test_study_rule_program__uniqueness(create_study_rule_db, db_session):
    """Check that the table enforces uniqueness of the study_rule_id and program_name."""
    db_session.add(studyrule.StudyRule(id=1618, name="asdf"))
    db_session.commit()

    db_session.add(studyrule.StudyRuleProgram(study_rule_id=1618, program_name="dupe"))
    db_session.commit()

    with pytest.raises(exc.IntegrityError, match=r"study_rule_program_pk"):
        db_session.add(studyrule.StudyRuleProgram(study_rule_id=1618, program_name="dupe"))
        db_session.commit()


def test_study_rule_program__defaults_created_datetime(create_study_rule_db, db_session):
    db_session.add(studyrule.StudyRule(id=1618, name="asdf"))
    db_session.commit()

    db_session.add(studyrule.StudyRuleProgram(study_rule_id=1618, program_name="alpha"))
    db_session.commit()
    s = db_session.query(studyrule.StudyRuleProgram).filter(
        studyrule.StudyRuleProgram.study_rule_id == 1618 and studyrule.StudyRuleProgram.program_name == "alpha").one()
    assert s.created_datetime is not None


def test_study_rule_program__defaults_updated_datetime(create_study_rule_db, db_session):
    db_session.add(studyrule.StudyRule(id=1618, name="asdf"))
    db_session.commit()

    db_session.add(studyrule.StudyRuleProgram(study_rule_id=1618, program_name="alpha"))
    db_session.commit()
    s = db_session.query(studyrule.StudyRuleProgram).filter(
        studyrule.StudyRuleProgram.study_rule_id == 1618 and studyrule.StudyRuleProgram.program_name == "alpha").one()
    assert s.updated_datetime is not None


def test_study_rule_program__updates_updated_datetime(create_study_rule_db, db_session):
    db_session.add(studyrule.StudyRule(id=1618, name="asdf"))
    db_session.commit()

    db_session.add(studyrule.StudyRuleProgram(study_rule_id=1618, program_name="alpha"))
    db_session.commit()

    db_session.query(studyrule.StudyRuleProgram).filter(studyrule.StudyRuleProgram.study_rule_id == 1618).update(
        {"program_name": "updated"})
    db_session.commit()

    updated = db_session.query(studyrule.StudyRuleProgram).filter(
        studyrule.StudyRuleProgram.study_rule_id == 1618).one()
    assert updated.updated_datetime > updated.created_datetime


def test_study_rule_program__to_json():
    sp = studyrule.StudyRuleProgram(
        study_rule_id=1618,
        program_name="alpha",
        created_datetime=datetime.datetime(
            year=2020,
            month=4,
            day=15,
            hour=12,
            minute=45,
            second=21,
            microsecond=123,
            tzinfo=pytz.utc,
        ),
        updated_datetime=datetime.datetime(
            year=2020,
            month=4,
            day=16,
            hour=12,
            minute=45,
            second=21,
            microsecond=123,
            tzinfo=pytz.utc,
        )
    )
    expected = json.loads(json.dumps({
        "study_rule_id": 1618,
        "program_name": "alpha",
        "created_datetime": "2020-04-15T12:45:21.000123+00:00",
        "updated_datetime": "2020-04-16T12:45:21.000123+00:00",
    }))
    assert sp.to_json() == expected


def test_study_rule_program__to_json_without_dates():
    sp = studyrule.StudyRuleProgram(
        study_rule_id=1618,
        program_name="alpha",
    )
    expected = json.loads(json.dumps({
        "study_rule_id": 1618,
        "program_name": "alpha",
        "created_datetime": None,
        "updated_datetime": None,
    }))
    assert sp.to_json() == expected


def test_study_rule_program__str():
    sp = studyrule.StudyRuleProgram(
        study_rule_id=1618,
        program_name="alpha",
        created_datetime=datetime.datetime(
            year=2020,
            month=4,
            day=15,
            hour=12,
            minute=45,
            second=21,
            microsecond=123,
            tzinfo=pytz.utc,
        ),
        updated_datetime=datetime.datetime(
            year=2020,
            month=4,
            day=16,
            hour=12,
            minute=45,
            second=21,
            microsecond=123,
            tzinfo=pytz.utc,
        )
    )
    expected = "<StudyRuleProgram(study_rule_id=1618, program_name='alpha', created_datetime=2020-04-15T12:45:21.000123+00:00, updated_datetime=2020-04-16T12:45:21.000123+00:00)>"
    assert str(sp) == expected


def test_study_rule_program__str_without_dates():
    sp = studyrule.StudyRuleProgram(
        study_rule_id=1618,
        program_name="alpha",
    )
    expected = "<StudyRuleProgram(study_rule_id=1618, program_name='alpha', created_datetime=None, updated_datetime=None)>"
    assert str(sp) == expected


@pytest.mark.filterwarnings(
    "ignore:Column 'study_rule_program_project.study_rule_id' is marked as a member of the primary key for table 'study_rule_program_project'")
def test_study_rule_program_project__study_rule_id_must_be_defined(create_study_rule_db, db_session):
    with pytest.raises(exc.IntegrityError, match=r"violates not-null constraint"):
        db_session.add(studyrule.StudyRuleProgramProject(program_name="game_of_life", project_code="asdf"))
        db_session.commit()


@pytest.mark.filterwarnings(
    "ignore:Column 'study_rule_program_project.program_name' is marked as a member of the primary key for table 'study_rule_program_project'")
def test_study_rule_program_project__program_name_must_be_defined(create_study_rule_db, db_session):
    with pytest.raises(exc.IntegrityError, match=r"violates not-null constraint"):
        db_session.add(studyrule.StudyRuleProgramProject(study_rule_id=1618, project_code="asdf"))
        db_session.commit()


@pytest.mark.filterwarnings(
    "ignore:Column 'study_rule_program_project.project_code' is marked as a member of the primary key for table 'study_rule_program_project'")
def test_study_rule_program_project__project_code_must_be_defined(create_study_rule_db, db_session):
    with pytest.raises(exc.IntegrityError, match=r"violates not-null constraint"):
        db_session.add(studyrule.StudyRuleProgramProject(study_rule_id=1618, program_name="game_of_life"))
        db_session.commit()


def test_study_rule_program_project__study_rule_must_exist(create_study_rule_db, db_session):
    with pytest.raises(exc.IntegrityError, match=r"study_rule_program_project_study_rule_id_fk"):
        db_session.add(
            studyrule.StudyRuleProgramProject(study_rule_id=1618, program_name="game_of_life", project_code="asdf"))
        db_session.commit()


def test_study_rule_program_project__uniqueness(create_study_rule_db, db_session):
    """Check that the table enforces uniqueness of the study_rule_id, program_name, and project_code."""
    db_session.add(studyrule.StudyRule(id=1618, name="asdf"))
    db_session.commit()

    db_session.add(studyrule.StudyRuleProgramProject(study_rule_id=1618, program_name="dupe", project_code="dupe"))
    db_session.commit()

    with pytest.raises(exc.IntegrityError, match=r"study_rule_program_project_pk"):
        db_session.add(studyrule.StudyRuleProgramProject(study_rule_id=1618, program_name="dupe", project_code="dupe"))
        db_session.commit()


def test_study_rule_program_project__study_rule_can_have_multiple_programs_and_projects(create_study_rule_db,
        db_session):
    db_session.add(studyrule.StudyRule(id=1618, name="asdf"))
    db_session.commit()

    db_session.add(studyrule.StudyRuleProgramProject(study_rule_id=1618, program_name="alpha", project_code="uno"))
    db_session.add(studyrule.StudyRuleProgramProject(study_rule_id=1618, program_name="alpha", project_code="dos"))
    db_session.add(studyrule.StudyRuleProgramProject(study_rule_id=1618, program_name="beta", project_code="uno"))
    db_session.add(studyrule.StudyRuleProgramProject(study_rule_id=1618, program_name="beta", project_code="dos"))
    db_session.commit()

    assert db_session.query(studyrule.StudyRuleProgramProject).filter(
        studyrule.StudyRuleProgramProject.study_rule_id == 1618).count() == 4


def test_study_rule_program_project__defaults_created_datetime (create_study_rule_db, db_session):
    db_session.add(studyrule.StudyRule(id=1618, name="asdf"))
    db_session.commit()

    db_session.add(studyrule.StudyRuleProgramProject(study_rule_id=1618, program_name="alpha", project_code="uno"))
    db_session.commit()
    s = db_session.query(studyrule.StudyRuleProgramProject) \
        .filter(studyrule.StudyRuleProgramProject.study_rule_id == 1618
                and studyrule.StudyRuleProgramProject.program_name == "alpha"
                and studyrule.StudyRuleProgramProject.project_code == "uno") \
        .one()
    assert s.created_datetime  is not None


def test_study_rule_program_project__defaults_updated_datetime (create_study_rule_db, db_session):
    db_session.add(studyrule.StudyRule(id=1618, name="asdf"))
    db_session.commit()

    db_session.add(studyrule.StudyRuleProgramProject(study_rule_id=1618, program_name="alpha", project_code="uno"))
    db_session.commit()
    s = db_session.query(studyrule.StudyRuleProgramProject) \
        .filter(studyrule.StudyRuleProgramProject.study_rule_id == 1618
                and studyrule.StudyRuleProgramProject.program_name == "alpha"
                and studyrule.StudyRuleProgramProject.project_code == "uno") \
        .one()
    assert s.updated_datetime is not None


def test_study_rule_program__updates_updated_datetime (create_study_rule_db, db_session):
    db_session.add(studyrule.StudyRule(id=1618, name="asdf"))
    db_session.commit()

    db_session.add(studyrule.StudyRuleProgramProject(study_rule_id=1618, program_name="alpha", project_code="uno"))
    db_session.commit()

    db_session.query(studyrule.StudyRuleProgramProject).filter(
        studyrule.StudyRuleProgramProject.study_rule_id == 1618).update(
        {"project_code": "updated"})
    db_session.commit()

    updated = db_session.query(studyrule.StudyRuleProgramProject).filter(
        studyrule.StudyRuleProgramProject.study_rule_id == 1618).one()
    assert updated.updated_datetime > updated.created_datetime


def test_study_rule_program_project__to_json():
    spp = studyrule.StudyRuleProgramProject(
        study_rule_id=1618,
        program_name="alpha",
        project_code="uno",
        created_datetime=datetime.datetime(
            year=2020,
            month=4,
            day=15,
            hour=12,
            minute=45,
            second=21,
            microsecond=123,
            tzinfo=pytz.utc,
        ),
        updated_datetime=datetime.datetime(
            year=2020,
            month=4,
            day=16,
            hour=12,
            minute=45,
            second=21,
            microsecond=123,
            tzinfo=pytz.utc,
        )
    )
    expected = json.loads(json.dumps({
        "study_rule_id": 1618,
        "program_name": "alpha",
        "project_code": "uno",
        "created_datetime": "2020-04-15T12:45:21.000123+00:00",
        "updated_datetime": "2020-04-16T12:45:21.000123+00:00",
    }))
    assert spp.to_json() == expected


def test_study_rule_program_project__to_json_without_dates():
    spp = studyrule.StudyRuleProgramProject(
        study_rule_id=1618,
        program_name="alpha",
        project_code="uno",
    )
    expected = json.loads(json.dumps({
        "study_rule_id": 1618,
        "program_name": "alpha",
        "project_code": "uno",
        "created_datetime": None,
        "updated_datetime": None,
    }))
    assert spp.to_json() == expected


def test_study_rule_program_project__str():
    spp = studyrule.StudyRuleProgramProject(
        study_rule_id=1618,
        program_name="alpha",
        project_code="uno",
        created_datetime=datetime.datetime(
            year=2020,
            month=4,
            day=15,
            hour=12,
            minute=45,
            second=21,
            microsecond=123,
            tzinfo=pytz.utc,
        ),
        updated_datetime=datetime.datetime(
            year=2020,
            month=4,
            day=16,
            hour=12,
            minute=45,
            second=21,
            microsecond=123,
            tzinfo=pytz.utc,
        )
    )
    expected = "<StudyRuleProgramProject(study_rule_id=1618, program_name='alpha', project_code='uno', created_datetime=2020-04-15T12:45:21.000123+00:00, updated_datetime=2020-04-16T12:45:21.000123+00:00)>"
    assert str(spp) == expected


def test_study_rule_program_project__str_without_dates():
    spp = studyrule.StudyRuleProgramProject(
        study_rule_id=1618,
        program_name="alpha",
        project_code="uno",
    )
    expected = "<StudyRuleProgramProject(study_rule_id=1618, program_name='alpha', project_code='uno', created_datetime=None, updated_datetime=None)>"
    assert str(spp) == expected
