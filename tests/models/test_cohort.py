import json
import uuid
import pytest
from gdc_ng_models.models import cohort
from sqlalchemy import exc


@pytest.fixture(scope="function")
def fixture_context(create_cohort_db, db_session):
    """Create an anonymous context for use with other tests."""

    db_session.add(cohort.AnonymousContext(name="test_context"))
    db_session.commit()
    return db_session.query(cohort.AnonymousContext).filter(
        cohort.AnonymousContext.name == "test_context").one()


def test_anonymous_context__valid_create(create_cohort_db, db_session):
    """Tests creation of a valid anonymous context entity."""

    expected_id = uuid.uuid4()
    expected_name = "test_context"

    db_session.add(cohort.AnonymousContext(
        id=expected_id,
        name=expected_name,
    ))
    db_session.commit()

    context = db_session.query(cohort.AnonymousContext).filter(
        cohort.AnonymousContext.name == expected_name).one()

    assert context.id == expected_id
    assert context.name == expected_name


def test_anonymous_context__unique_ids(create_cohort_db, db_session):
    """Tests unique constraint on anonymous context ID."""

    target_id = uuid.uuid4()
    db_session.add(cohort.AnonymousContext(
        id=target_id,
        name="context_1",
    ))
    db_session.commit()

    with pytest.raises(exc.IntegrityError, match=r"anonymous_context_pkey"):
        db_session.add(cohort.AnonymousContext(
            id=target_id,
            name="context_2",
        ))
        db_session.commit()


def test_anonymous_context__defaults_unique_ids(create_cohort_db, db_session):
    """Tests default generated IDs on anonymous context are unique."""

    db_session.add(cohort.AnonymousContext(name="context_1"))
    db_session.add(cohort.AnonymousContext(name="context_2"))
    db_session.commit()

    context_1 = db_session.query(cohort.AnonymousContext).filter(
        cohort.AnonymousContext.name == "context_1").one()
    context_2 = db_session.query(cohort.AnonymousContext).filter(
        cohort.AnonymousContext.name == "context_2").one()

    assert context_1.id is not None
    assert context_2.id is not None
    assert context_1.id != context_2.id


def test_anonymous_context__name_not_nullable(create_cohort_db, db_session):
    """Tests name must be defined for anonymous context."""

    with pytest.raises(exc.IntegrityError, match=r"violates not-null constraint"):
        db_session.add(cohort.AnonymousContext(id=uuid.uuid4()))
        db_session.commit()


def test_anonymous_context__to_json(create_cohort_db, db_session):
    """Tests json output for anonymous context is valid."""

    db_session.add(cohort.AnonymousContext(name="test_context"))
    db_session.commit()

    test_context = db_session.query(cohort.AnonymousContext).filter(
        cohort.AnonymousContext.name == "test_context").one()

    expected_json = json.loads(json.dumps({
        "id": str(test_context.id),
        "name": test_context.name,
        "created_datetime": test_context.created_datetime.isoformat(),
        "updated_datetime": test_context.updated_datetime.isoformat(),
    }))

    assert test_context.to_json() == expected_json


def test_cohort__valid_create(create_cohort_db, db_session, fixture_context):
    """Tests creation of a valid cohort entity."""

    # define expected values
    expected_id = uuid.uuid4()
    expected_name = "test_cohort"
    expected_context_id = fixture_context.id
    expected_current_filter_id = 1

    # create and retrieve cohort
    db_session.add(cohort.Cohort(
        id=expected_id,
        name=expected_name,
        context_id=expected_context_id,
        current_filter_id=expected_current_filter_id,
    ))
    db_session.commit()
    test_cohort = db_session.query(cohort.Cohort).filter(
        cohort.Cohort.name == expected_name).one()

    # validate cohort
    assert test_cohort.id == expected_id
    assert test_cohort.name == expected_name
    assert test_cohort.context_id == expected_context_id
    assert test_cohort.current_filter_id == expected_current_filter_id


def test_cohort__context_fkey_constraint(create_cohort_db, db_session):
    """Tests cohort foreign key constraint on context_id."""

    non_existent_id = uuid.uuid4()
    with pytest.raises(exc.IntegrityError, match=r"cohort_context_id_fkey"):
        db_session.add(cohort.Cohort(
            name="test_cohort_1",
            context_id=non_existent_id,
            current_filter_id=1,
        ))
        db_session.commit()


def test_cohort__unique_ids(create_cohort_db, db_session, fixture_context):
    """Tests unique constraint on cohort ID."""

    target_id = uuid.uuid4()
    db_session.add(cohort.Cohort(
        id=target_id,
        name="test_cohort_1",
        context_id=fixture_context.id,
        current_filter_id=1,
    ))
    db_session.commit()

    with pytest.raises(exc.IntegrityError, match=r"cohort_pkey"):
        db_session.add(cohort.Cohort(
            id=target_id,
            name="test_cohort_2",
            context_id=fixture_context.id,
            current_filter_id=1,
        ))
        db_session.commit()


def test_cohort__defaults_unique_ids(create_cohort_db, db_session, fixture_context):
    """Tests default generated IDs on cohort are unique."""

    db_session.add(cohort.Cohort(
        name="cohort_1",
        context_id=fixture_context.id,
        current_filter_id=1,
    ))
    db_session.add(cohort.Cohort(
        name="cohort_2",
        context_id=fixture_context.id,
        current_filter_id=2,
    ))
    db_session.commit()

    cohort_1 = db_session.query(cohort.Cohort).filter(
        cohort.Cohort.name == "cohort_1").one()
    cohort_2 = db_session.query(cohort.Cohort).filter(
        cohort.Cohort.name == "cohort_2").one()

    assert cohort_1.id is not None
    assert cohort_2.id is not None
    assert cohort_1.id != cohort_2.id


def test_cohort__name_not_nullable(create_cohort_db, db_session, fixture_context):
    """Tests name must be defined for cohort."""

    with pytest.raises(exc.IntegrityError, match=r"violates not-null constraint"):
        db_session.add(cohort.Cohort(
            id=uuid.uuid4(),
            context_id=fixture_context.id,
            current_filter_id=1,
        ))
        db_session.commit()


def test_cohort__to_json(create_cohort_db, db_session, fixture_context):
    """Tests json output for cohort is valid."""

    db_session.add(cohort.Cohort(
        name="test_cohort",
        id=uuid.uuid4(),
        context_id=fixture_context.id,
        current_filter_id=1,
    ))
    db_session.commit()

    test_cohort = db_session.query(cohort.Cohort).filter(
        cohort.Cohort.name == "test_cohort").one()

    expected_json = json.loads(json.dumps({
        "id": str(test_cohort.id),
        "name": test_cohort.name,
        "context_id": str(test_cohort.context_id),
        "current_filter_id": test_cohort.current_filter_id,
        "created_datetime": test_cohort.created_datetime.isoformat(),
        "updated_datetime": test_cohort.updated_datetime.isoformat(),
    }))

    assert test_cohort.to_json() == expected_json
