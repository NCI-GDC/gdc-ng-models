import datetime
import json

import pytest
import pytz
from sqlalchemy import exc

from gdc_ng_models.models import study


def test_study__defaults_unique_ids(create_study_db, db_session):
    db_session.add(study.Study(name="first"))
    db_session.add(study.Study(name="second"))
    db_session.commit()

    first = db_session.query(study.Study).filter(study.Study.name == "first").first()
    second = db_session.query(study.Study).filter(study.Study.name == "second").first()
    assert first.id is not None
    assert second.id is not None
    assert first.id != second.id


def test_study__unique_id(create_study_db, db_session):
    db_session.add(study.Study(id=1618, name="first"))
    db_session.commit()

    with pytest.raises(exc.IntegrityError, match=r"study_pk"):
        db_session.add(study.Study(id=1618, name="second"))
        db_session.commit()


def test_study__name_must_be_defined(create_study_db, db_session):
    with pytest.raises(exc.IntegrityError, match=r"violates not-null constraint"):
        db_session.add(study.Study(id=1618))
        db_session.commit()


def test_study__unique_name(create_study_db, db_session):
    db_session.add(study.Study(name="dupe"))
    db_session.commit()

    with pytest.raises(exc.IntegrityError, match=r"study_name_idx"):
        db_session.add(study.Study(name="dupe"))
        db_session.commit()


def test_study__defaults_created_date(create_study_db, db_session):
    db_session.add(study.Study(name="asdf"))
    db_session.commit()
    s = db_session.query(study.Study).filter(study.Study.name == "asdf").first()
    assert s.created_date is not None


def test_study__defaults_updated_date(create_study_db, db_session):
    db_session.add(study.Study(name="asdf"))
    db_session.commit()
    s = db_session.query(study.Study).filter(study.Study.name == "asdf").first()
    assert s.updated_date is not None


def test_study__to_json():
    s = study.Study(
        id=1618,
        name="asdf",
        created_date=datetime.datetime(
            year=2020,
            month=4,
            day=15,
            hour=12,
            minute=45,
            second=21,
            microsecond=123,
            tzinfo=pytz.utc,
        ),
        updated_date=datetime.datetime(
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
        "created_date": "2020-04-15T12:45:21.000123+00:00",
        "updated_date": "2020-04-16T12:45:21.000123+00:00",
    }))
    assert s.to_json() == expected


def test_study__str():
    s = study.Study(
        id=1618,
        name="asdf",
        created_date=datetime.datetime(
            year=2020,
            month=4,
            day=15,
            hour=12,
            minute=45,
            second=21,
            microsecond=123,
            tzinfo=pytz.utc,
        ),
        updated_date=datetime.datetime(
            year=2020,
            month=4,
            day=16,
            hour=12,
            minute=45,
            second=21,
            microsecond=123,
            tzinfo=pytz.utc,
        ))
    expected = "<Study(id=1618, name='asdf', created_date=2020-04-15T12:45:21.000123+00:00, updated_date=2020-04-16T12:45:21.000123+00:00)>"
    assert str(s) == expected


def test_study_program__study_must_exist(create_study_db, db_session):
    with pytest.raises(exc.IntegrityError, match=r"study_program_study_id_fk"):
        db_session.add(study.StudyProgram(study_id=1618, program_name="game_of_life"))
        db_session.commit()


@pytest.mark.filterwarnings(
    "ignore:Column 'study_program.study_id' is marked as a member of the primary key for table 'study_program'")
def test_study_program__study_id_must_be_defined(create_study_db, db_session):
    with pytest.raises(exc.IntegrityError, match=r"violates not-null constraint"):
        db_session.add(study.StudyProgram(program_name="game_of_life"))
        db_session.commit()


@pytest.mark.filterwarnings(
    "ignore:Column 'study_program.program_name' is marked as a member of the primary key for table 'study_program'")
def test_study_program__program_name_must_be_defined(create_study_db, db_session):
    with pytest.raises(exc.IntegrityError, match=r"violates not-null constraint"):
        db_session.add(study.StudyProgram(study_id=1618))
        db_session.commit()


def test_study_program__study_can_contain_multiple_programs(create_study_db, db_session):
    db_session.add(study.Study(id=1618, name="asdf"))
    db_session.commit()

    db_session.add(study.StudyProgram(study_id=1618, program_name="alpha"))
    db_session.add(study.StudyProgram(study_id=1618, program_name="beta"))
    db_session.commit()

    assert db_session.query(study.StudyProgram).filter(study.StudyProgram.study_id == 1618).count() == 2


def test_study_program__uniqueness(create_study_db, db_session):
    """Check that the table enforces uniqueness of the study_id and program_name."""
    db_session.add(study.Study(id=1618, name="asdf"))
    db_session.commit()

    db_session.add(study.StudyProgram(study_id=1618, program_name="dupe"))
    db_session.commit()

    with pytest.raises(exc.IntegrityError, match=r"study_program_pk"):
        db_session.add(study.StudyProgram(study_id=1618, program_name="dupe"))
        db_session.commit()


def test_study_program__defaults_created_date(create_study_db, db_session):
    db_session.add(study.Study(id=1618, name="asdf"))
    db_session.commit()

    db_session.add(study.StudyProgram(study_id=1618, program_name="alpha"))
    db_session.commit()
    s = db_session.query(study.StudyProgram).filter(study.StudyProgram.study_id == 1618 and study.StudyProgram.program_name == "alpha").first()
    assert s.created_date is not None


def test_study_program__defaults_updated_date(create_study_db, db_session):
    db_session.add(study.Study(id=1618, name="asdf"))
    db_session.commit()

    db_session.add(study.StudyProgram(study_id=1618, program_name="alpha"))
    db_session.commit()
    s = db_session.query(study.StudyProgram).filter(study.StudyProgram.study_id == 1618 and study.StudyProgram.program_name == "alpha").first()
    assert s.updated_date is not None


def test_study_program__to_json():
    sp = study.StudyProgram(
        study_id=1618,
        program_name="alpha",
        created_date=datetime.datetime(
            year=2020,
            month=4,
            day=15,
            hour=12,
            minute=45,
            second=21,
            microsecond=123,
            tzinfo=pytz.utc,
        ),
        updated_date=datetime.datetime(
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
        "study_id": 1618,
        "program_name": "alpha",
        "created_date": "2020-04-15T12:45:21.000123+00:00",
        "updated_date": "2020-04-16T12:45:21.000123+00:00",
    }))
    assert sp.to_json() == expected


def test_study_program__str():
    sp = study.StudyProgram(
        study_id=1618,
        program_name="alpha",
        created_date=datetime.datetime(
            year=2020,
            month=4,
            day=15,
            hour=12,
            minute=45,
            second=21,
            microsecond=123,
            tzinfo=pytz.utc,
        ),
        updated_date=datetime.datetime(
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
    expected = "<StudyProgram(study_id=1618, program_name='alpha', created_date=2020-04-15T12:45:21.000123+00:00, updated_date=2020-04-16T12:45:21.000123+00:00)>"
    assert str(sp) == expected


@pytest.mark.filterwarnings(
    "ignore:Column 'study_program_project.study_id' is marked as a member of the primary key for table 'study_program_project'")
def test_study_program_project__study_id_must_be_defined(create_study_db, db_session):
    with pytest.raises(exc.IntegrityError, match=r"violates not-null constraint"):
        db_session.add(study.StudyProgramProject(program_name="game_of_life", project_code="asdf"))
        db_session.commit()


@pytest.mark.filterwarnings(
    "ignore:Column 'study_program_project.program_name' is marked as a member of the primary key for table 'study_program_project'")
def test_study_program_project__program_name_must_be_defined(create_study_db, db_session):
    with pytest.raises(exc.IntegrityError, match=r"violates not-null constraint"):
        db_session.add(study.StudyProgramProject(study_id=1618, project_code="asdf"))
        db_session.commit()


@pytest.mark.filterwarnings(
    "ignore:Column 'study_program_project.project_code' is marked as a member of the primary key for table 'study_program_project'")
def test_study_program_project__project_code_must_be_defined(create_study_db, db_session):
    with pytest.raises(exc.IntegrityError, match=r"violates not-null constraint"):
        db_session.add(study.StudyProgramProject(study_id=1618, program_name="game_of_life"))
        db_session.commit()


def test_study_program_project__study_must_exist(create_study_db, db_session):
    with pytest.raises(exc.IntegrityError, match=r"study_program_project_study_id_fk"):
        db_session.add(study.StudyProgramProject(study_id=1618, program_name="game_of_life", project_code="asdf"))
        db_session.commit()


def test_study_program_project__uniqueness(create_study_db, db_session):
    """Check that the table enforces uniqueness of the study_id, program_name, and project_code."""
    db_session.add(study.Study(id=1618, name="asdf"))
    db_session.commit()

    with pytest.raises(exc.IntegrityError, match=r"study_program_project_pk"):
        db_session.add(study.StudyProgramProject(study_id=1618, program_name="dupe", project_code="dupe"))
        db_session.add(study.StudyProgramProject(study_id=1618, program_name="dupe", project_code="dupe"))
        db_session.commit()


def test_study_program_project__study_can_have_multiple_programs_and_projects(create_study_db, db_session):
    db_session.add(study.Study(id=1618, name="asdf"))
    db_session.commit()

    db_session.add(study.StudyProgramProject(study_id=1618, program_name="alpha", project_code="uno"))
    db_session.add(study.StudyProgramProject(study_id=1618, program_name="alpha", project_code="dos"))
    db_session.add(study.StudyProgramProject(study_id=1618, program_name="beta", project_code="uno"))
    db_session.add(study.StudyProgramProject(study_id=1618, program_name="beta", project_code="dos"))
    db_session.commit()

    assert db_session.query(study.StudyProgramProject).filter(study.StudyProgramProject.study_id == 1618).count() == 4


def test_study_program_project__defaults_created_date(create_study_db, db_session):
    db_session.add(study.Study(id=1618, name="asdf"))
    db_session.commit()

    db_session.add(study.StudyProgramProject(study_id=1618, program_name="alpha", project_code="uno"))
    db_session.commit()
    s = db_session.query(study.StudyProgramProject)\
        .filter(study.StudyProgramProject.study_id == 1618
                and study.StudyProgramProject.program_name == "alpha"
                and study.StudyProgramProject.project_code == "uno")\
        .first()
    assert s.created_date is not None


def test_study_program_project__defaults_updated_date(create_study_db, db_session):
    db_session.add(study.Study(id=1618, name="asdf"))
    db_session.commit()

    db_session.add(study.StudyProgramProject(study_id=1618, program_name="alpha", project_code="uno"))
    db_session.commit()
    s = db_session.query(study.StudyProgramProject)\
        .filter(study.StudyProgramProject.study_id == 1618
                and study.StudyProgramProject.program_name == "alpha"
                and study.StudyProgramProject.project_code == "uno")\
        .first()
    assert s.updated_date is not None


def test_study_program_project__to_json():
    spp = study.StudyProgramProject(
        study_id=1618,
        program_name="alpha",
        project_code="uno",
        created_date=datetime.datetime(
            year=2020,
            month=4,
            day=15,
            hour=12,
            minute=45,
            second=21,
            microsecond=123,
            tzinfo=pytz.utc,
        ),
        updated_date=datetime.datetime(
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
        "study_id": 1618,
        "program_name": "alpha",
        "project_code": "uno",
        "created_date": "2020-04-15T12:45:21.000123+00:00",
        "updated_date": "2020-04-16T12:45:21.000123+00:00",
    }))
    assert spp.to_json() == expected


def test_study_program_project__str():
    spp = study.StudyProgramProject(
        study_id=1618,
        program_name="alpha",
        project_code="uno",
        created_date=datetime.datetime(
            year=2020,
            month=4,
            day=15,
            hour=12,
            minute=45,
            second=21,
            microsecond=123,
            tzinfo=pytz.utc,
        ),
        updated_date=datetime.datetime(
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
    expected = "<StudyProgramProject(study_id=1618, program_name='alpha', project_code='uno', created_date=2020-04-15T12:45:21.000123+00:00, updated_date=2020-04-16T12:45:21.000123+00:00)>"
    assert str(spp) == expected
