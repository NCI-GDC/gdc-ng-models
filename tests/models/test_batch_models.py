import datetime
import json

import pytest
import pytz
from sqlalchemy import exc

from gdc_ng_models.models import batch


@pytest.fixture(scope="function")
def test_batches(create_batch_db, db_session):
    b1 = batch.Batch(name="a", project_id="GDC-MISC")
    b2 = batch.Batch(name="b", project_id="GDC-INTERNAL")
    db_session.add(b1)
    db_session.add(b2)
    db_session.commit()

    yield (b1, b2)


@pytest.fixture(scope="function")
def test_batches_with_members(create_batch_db, db_session):
    b1 = batch.Batch(name="a", project_id="GDC-MISC")
    b2 = batch.Batch(name="b", project_id="GDC-INTERNAL")
    db_session.add(b1)
    db_session.add(b2)
    db_session.commit()

    b1.members.append(batch.BatchMembership(node_id="node_1"))
    b1.members.append(batch.BatchMembership(node_id="node_2"))
    b2.members.append(batch.BatchMembership(node_id="node_3"))
    b2.members.append(batch.BatchMembership(node_id="node_4"))
    db_session.commit()

    yield (b1, b2)


def test_batch__defaults_unique_ids(create_batch_db, db_session):
    db_session.add(batch.Batch(name="a", project_id="GDC-MISC"))
    db_session.add(batch.Batch(name="b", project_id="GDC-MISC"))
    db_session.commit()

    first = db_session.query(batch.Batch).filter(batch.Batch.name == "a").one()
    second = db_session.query(batch.Batch).filter(batch.Batch.name == "b").one()
    assert first.id is not None
    assert second.id is not None
    assert first.id != second.id


@pytest.mark.parametrize(
    "attribute",
    ["created_datetime", "updated_datetime"],
    ids=["default_created_datetime", "default_updated_datetime"],
)
def test_batch__default_datetimes(create_batch_db, db_session, attribute):
    db_session.add(batch.Batch(name="a", project_id="GDC-MISC"))
    db_session.commit()
    b = db_session.query(batch.Batch).filter(batch.Batch.name == "a").one()
    date = getattr(b, attribute)
    assert date is not None


def test_batch__default_status(create_batch_db, db_session):
    db_session.add(batch.Batch(name="a", project_id="GDC-MISC"))
    db_session.commit()
    b = db_session.query(batch.Batch).filter(batch.Batch.name == "a").one()
    assert b.status == "OPEN"


@pytest.mark.parametrize(
    "status, expected",
    [("PENDING", "invalid status specified"), ("", "status is required")],
    ids=["incorrect_status", "empty_status"],
)
def test_batch__status_values(create_batch_db, db_session, status, expected):
    with pytest.raises(ValueError, match=r"{}".format(expected)):
        db_session.add(batch.Batch(name="a", project_id="GDC-MISC", status=status))
        db_session.commit()


def test_batch__updates(create_batch_db, db_session):
    b = batch.Batch(name="a", project_id="GDC-MISC")
    db_session.add(b)
    db_session.commit()
    b.project_id = "GDC-INTERNAL"
    db_session.commit()

    updated_b = db_session.query(batch.Batch).filter(batch.Batch.name == "a").one()
    assert updated_b.project_id == "GDC-INTERNAL"
    assert updated_b.updated_datetime > updated_b.created_datetime


def test_batch__repr():
    b = batch.Batch(
        id=1000,
        name="a",
        project_id="GDC-MISC",
        status="CLOSED",
        created_datetime=datetime.datetime(
            year=2021,
            month=1,
            day=18,
            hour=9,
            minute=30,
            second=10,
            microsecond=123,
            tzinfo=pytz.utc,
        ),
        updated_datetime=datetime.datetime(
            year=2021,
            month=1,
            day=18,
            hour=9,
            minute=30,
            second=10,
            microsecond=123,
            tzinfo=pytz.utc,
        ),
    )
    expected = "<Batch(id='1000', name='a', project_id='GDC-MISC', status='CLOSED', created_datetime='2021-01-18T09:30:10.000123+00:00', updated_datetime='2021-01-18T09:30:10.000123+00:00')>"
    assert repr(b) == expected


def test_batch__primary_key_constraint(create_batch_db, db_session):
    db_session.add(batch.Batch(id=1000, name="a", project_id="GDC-MISC"))
    db_session.commit()

    with pytest.raises(exc.IntegrityError, match=r"batch_pk"):
        db_session.add(batch.Batch(id=1000, name="b", project_id="GDC-INTERNAL"))
        db_session.commit()


@pytest.mark.parametrize(
    "contents",
    [
        {"project_id": "GDC-MISC"},
        {"name": "a"},
    ],
    ids=["name_must_be_defined", "project_id_must_be_defined"],
)
def test_batch__required_fields(create_batch_db, db_session, contents):
    with pytest.raises(exc.IntegrityError, match=r"violates not-null constraint"):
        db_session.add(batch.Batch(**contents))
        db_session.commit()


@pytest.mark.parametrize(
    "contents, expected",
    [
        (
            {
                "id": 1000,
                "name": "a",
                "project_id": "GDC-MISC",
                "status": "CLOSED",
                "created_datetime": datetime.datetime(
                    year=2021,
                    month=1,
                    day=18,
                    hour=9,
                    minute=30,
                    second=10,
                    microsecond=123,
                    tzinfo=pytz.utc,
                ),
                "updated_datetime": datetime.datetime(
                    year=2021,
                    month=1,
                    day=18,
                    hour=10,
                    minute=30,
                    second=10,
                    microsecond=123,
                    tzinfo=pytz.utc,
                ),
            },
            json.loads(
                json.dumps(
                    {
                        "id": 1000,
                        "name": "a",
                        "project_id": "GDC-MISC",
                        "status": "CLOSED",
                        "created_datetime": "2021-01-18T09:30:10.000123+00:00",
                        "updated_datetime": "2021-01-18T10:30:10.000123+00:00",
                    }
                )
            ),
        ),
        (
            {
                "id": 1000,
                "name": "a",
                "project_id": "GDC-MISC",
            },
            json.loads(
                json.dumps(
                    {
                        "id": 1000,
                        "name": "a",
                        "project_id": "GDC-MISC",
                        "status": None,
                        "created_datetime": None,
                        "updated_datetime": None,
                    }
                )
            ),
        ),
    ],
    ids=["with_datetimes", "no_datetimes"],
)
def test_batch__to_json(contents, expected):
    b = batch.Batch(**contents)

    assert b.to_json() == expected


def test_batch_membership__direct_create(create_batch_db, db_session, test_batches):
    b = test_batches[0]
    db_session.add(batch.BatchMembership(batch_id=b.id, node_id="node_1"))
    db_session.commit()

    bm = (
        db_session.query(batch.BatchMembership)
        .filter(batch.BatchMembership.batch_id == b.id)
        .one()
    )

    assert bm.batch_id == b.id
    assert bm.node_id == "node_1"
    assert bm.created_datetime is not None
    assert bm.updated_datetime is not None
    assert len(b.members) == 1


def test_batch_membership__indirect_create(create_batch_db, db_session, test_batches):
    b = test_batches[0]
    b.members.append(batch.BatchMembership(node_id="node_1"))
    db_session.commit()

    bm = (
        db_session.query(batch.BatchMembership)
        .filter(batch.BatchMembership.batch_id == b.id)
        .one()
    )

    assert bm.batch_id == b.id
    assert bm.node_id == "node_1"
    assert bm.created_datetime is not None
    assert bm.updated_datetime is not None
    assert len(b.members) == 1


@pytest.mark.parametrize(
    "attribute",
    ["created_datetime", "updated_datetime"],
    ids=["default_created_datetime", "default_updated_datetime"],
)
def test_batch_membership__default_datetimes(
    create_batch_db, db_session, test_batches, attribute
):
    b = test_batches[0]
    db_session.add(batch.BatchMembership(batch_id=b.id, node_id="node_1"))
    db_session.commit()
    b = db_session.query(batch.Batch).filter(batch.Batch.name == "a").one()
    date = getattr(b, attribute)
    assert date is not None


def test_batch_membership__updated_datetime(
    create_batch_db, db_session, test_batches_with_members
):
    b1 = test_batches_with_members[0]
    b2 = test_batches_with_members[1]

    db_session.query(batch.BatchMembership).filter(
        batch.BatchMembership.node_id == "node_1"
    ).update({"batch_id": b2.id})
    db_session.commit()

    bm = (
        db_session.query(batch.BatchMembership)
        .filter(batch.BatchMembership.node_id == "node_1")
        .one()
    )
    assert bm.updated_datetime > bm.created_datetime


def test_batch_membership__move_node_between_batches(
    create_batch_db, db_session, test_batches_with_members
):
    b1 = test_batches_with_members[0]
    b2 = test_batches_with_members[1]
    db_session.query(batch.BatchMembership).filter(
        batch.BatchMembership.node_id == "node_1"
    ).update({"batch_id": b2.id})
    db_session.commit()

    assert len(b1.members) == 1
    assert len(b2.members) == 3


def test_batch_membership__repr():
    b = batch.BatchMembership(
        batch_id=1000,
        node_id="node_1",
        created_datetime=datetime.datetime(
            year=2021,
            month=1,
            day=18,
            hour=9,
            minute=30,
            second=10,
            microsecond=123,
            tzinfo=pytz.utc,
        ),
        updated_datetime=datetime.datetime(
            year=2021,
            month=1,
            day=18,
            hour=9,
            minute=30,
            second=10,
            microsecond=123,
            tzinfo=pytz.utc,
        ),
    )
    expected = "<BatchMembership(batch_id='1000', node_id='node_1', created_datetime='2021-01-18T09:30:10.000123+00:00', updated_datetime='2021-01-18T09:30:10.000123+00:00')>"
    assert repr(b) == expected


def test_batch_membership__primary_key_constraint(
    create_batch_db, db_session, test_batches
):
    b = test_batches[0]
    db_session.add(batch.BatchMembership(batch_id=b.id, node_id="node_1"))
    db_session.commit()
    with pytest.raises(exc.IntegrityError, match=r"batch_membership_pk"):
        db_session.add(batch.BatchMembership(batch_id=b.id, node_id="node_1"))
        db_session.commit()


def test_batch_membership__foreign_key_constraint(create_batch_db, db_session):
    with pytest.raises(exc.IntegrityError, match=r"batch_membership_batch_id_fk"):
        db_session.add(batch.BatchMembership(batch_id=1, node_id="node_1"))
        db_session.commit()


def test_batch_membership__node_id_required(create_batch_db, db_session, test_batches):
    b = test_batches[0]
    with pytest.raises(exc.IntegrityError, match="violates not-null constraint"):
        db_session.add(batch.BatchMembership(batch_id=b.id))
        db_session.commit()


@pytest.mark.parametrize(
    "contents, expected",
    [
        (
            {
                "batch_id": 1000,
                "node_id": "node_1",
                "created_datetime": datetime.datetime(
                    year=2021,
                    month=1,
                    day=18,
                    hour=9,
                    minute=30,
                    second=10,
                    microsecond=123,
                    tzinfo=pytz.utc,
                ),
                "updated_datetime": datetime.datetime(
                    year=2021,
                    month=1,
                    day=18,
                    hour=10,
                    minute=30,
                    second=10,
                    microsecond=123,
                    tzinfo=pytz.utc,
                ),
            },
            json.loads(
                json.dumps(
                    {
                        "batch_id": 1000,
                        "node_id": "node_1",
                        "created_datetime": "2021-01-18T09:30:10.000123+00:00",
                        "updated_datetime": "2021-01-18T10:30:10.000123+00:00",
                    }
                )
            ),
        ),
        (
            {
                "batch_id": 1000,
                "node_id": "node_1",
            },
            json.loads(
                json.dumps(
                    {
                        "batch_id": 1000,
                        "node_id": "node_1",
                        "created_datetime": None,
                        "updated_datetime": None,
                    }
                )
            ),
        ),
    ],
    ids=["with_datetimes", "no_datetimes"],
)
def test_batch__membership_to_json(contents, expected):
    b = batch.BatchMembership(**contents)

    assert b.to_json() == expected


def test_batch_membership__node_in_multiple_batches(
    create_batch_db, db_session, test_batches
):
    b1 = test_batches[0]
    b2 = test_batches[1]

    b1.members.append(batch.BatchMembership(node_id="node_1"))
    b2.members.append(batch.BatchMembership(node_id="node_1"))
    db_session.commit()

    bm1 = (
        db_session.query(batch.BatchMembership)
        .filter(batch.BatchMembership.batch_id == b1.id)
        .one()
    )

    bm2 = (
        db_session.query(batch.BatchMembership)
        .filter(batch.BatchMembership.batch_id == b2.id)
        .one()
    )

    assert b1.members[0].node_id == bm1.node_id
    assert b2.members[0].node_id == bm2.node_id


def test_batch_membership__delete_parent(
    create_batch_db, db_session, test_batches_with_members
):
    with pytest.raises(
        AssertionError,
        match=r"Dependency rule tried to blank-out primary key column",
    ):
        b = test_batches_with_members[0]
        db_session.delete(b)
        db_session.commit()


def test_batch_membership__delete_members(
    create_batch_db, db_session, test_batches_with_members
):
    b1 = test_batches_with_members[0]
    b2 = test_batches_with_members[1]

    db_session.query(batch.BatchMembership).filter(
        batch.BatchMembership.batch_id == b1.id
    ).delete()
    db_session.commit()

    assert db_session.query(batch.Batch).filter(batch.Batch.id == b1.id).one() == b1
    assert (
        len(
            db_session.query(batch.BatchMembership)
            .filter(batch.BatchMembership.batch_id == b1.id)
            .all()
        )
        == 0
    )
    assert db_session.query(batch.Batch).filter(batch.Batch.id == b2.id).one() == b2
    assert (
        len(
            db_session.query(batch.BatchMembership)
            .filter(batch.BatchMembership.batch_id == b2.id)
            .all()
        )
        == 2
    )


def test_batch_membership__delete_orphan(
    create_batch_db, db_session, test_batches_with_members
):
    with pytest.raises(
        AssertionError, match=r"Dependency rule tried to blank-out primary key column"
    ):
        b = test_batches_with_members[0]
        b.members.pop()
        db_session.commit()
        i