import json
import pytest
from gdc_ng_models.models import cohort
from sqlalchemy import exc


def test_anonymous_context__unique_ids(create_cohort_db, db_session):
    """Tests unique constraint on anonymous context ID."""

    db_session.add(cohort.AnonymousContext(
        id="8204edfc-a09b-473d-bcc2-2a8359859874",
        name="test_context_1"))
    db_session.commit()

    with pytest.raises(exc.IntegrityError, match=r"anonymous_context_pkey"):
        db_session.add(cohort.AnonymousContext(
            id="8204edfc-a09b-473d-bcc2-2a8359859874",
            name="test_context_2"))
        db_session.commit()


def test_anonymous_context__defaults_unique_ids(create_cohort_db, db_session):
    """Tests default generated IDs on anonymous context are unique."""

    db_session.add(cohort.AnonymousContext(name="test_context_1"))
    db_session.add(cohort.AnonymousContext(name="test_context_2"))
    db_session.commit()

    context_1 = db_session.query(cohort.AnonymousContext).filter(
        cohort.AnonymousContext.name == "test_context_1").one()
    context_2 = db_session.query(cohort.AnonymousContext).filter(
        cohort.AnonymousContext.name == "test_context_2").one()

    assert context_1.id is not None
    assert context_2.id is not None
    assert context_1.id != context_2.id


def test_anonymous_context__name_not_nullable(create_cohort_db, db_session):
    """Tests name must be defined for anonymous context."""

    with pytest.raises(exc.IntegrityError, match=r"violates not-null constraint"):
        db_session.add(cohort.AnonymousContext(id="8204edfc-a09b-473d-bcc2-2a8359859874"))
        db_session.commit()


def test_anonymous_context__to_json(create_cohort_db, db_session):
    """Tests json output for anonymous context is valid."""

    db_session.add(cohort.AnonymousContext(name="test_context_1"))
    db_session.commit()

    test_context = db_session.query(cohort.AnonymousContext).filter(
        cohort.AnonymousContext.name == "test_context_1").one()

    expected_json = json.loads(json.dumps({
            'id': str(test_context.id),
            'name': test_context.name,
            'created_datetime': test_context.created_datetime.isoformat(),
            'updated_datetime': test_context.updated_datetime.isoformat()
        }))

    assert test_context.to_json() == expected_json
