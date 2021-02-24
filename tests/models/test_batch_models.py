import datetime
import pytz
import json
import pytest

from gdc_ng_models.models import batch
from sqlalchemy import exc


def assert_db_state_after_delete(session, b1, b2):
    assert (
        len(
            session.query(batch.BatchMembership)
            .filter(batch.BatchMembership.batch_id == b1.id)
            .all()
        )
        == 0
    )
    b = session.query(batch.Batch).filter(batch.Batch.id == b2.id).one()
    assert b == b2
    bms = session.query(batch.BatchMembership).filter(batch.Batch.id == b2.id).all()
    assert len(bms) == 2


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

    b1.members.append(batch.BatchMembership(node_id="node_1", node_type="rma"))
    b1.members.append(batch.BatchMembership(node_id="node_2", node_type="rma"))
    b2.members.append(batch.BatchMembership(node_id="node_3", node_type="sur"))
    b2.members.append(batch.BatchMembership(node_id="node_4", node_type="sur"))
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


def test_batch__defaults_created_datetime(create_batch_db, db_session):
    db_session.add(batch.Batch(name="a", project_id="GDC-MISC"))
    db_session.commit()
    b = db_session.query(batch.Batch).filter(batch.Batch.name == "a").one()
    assert b.created_datetime is not None


def test_batch__primary_key_constraint(create_batch_db, db_session):
    db_session.add(batch.Batch(id=1000, name="a", project_id="GDC-MISC"))
    db_session.commit()

    with pytest.raises(exc.IntegrityError, match=r"batch_pk"):
        db_session.add(batch.Batch(id=1000, name="a", project_id="GDC-MISC"))
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
            },
            json.loads(
                json.dumps(
                    {
                        "id": 1000,
                        "name": "a",
                        "project_id": "GDC-MISC",
                        "created_datetime": "2021-01-18T09:30:10.000123+00:00",
                    }
                )
            ),
        ),
        (
            {
                "id": 1000,
                "name": "a",
                "project_id": "GDC-MISC",
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
            },
            json.loads(
                json.dumps(
                    {
                        "id": 1000,
                        "name": "a",
                        "project_id": "GDC-MISC",
                        "created_datetime": "2021-01-18T09:30:10.000123+00:00",
                    }
                )
            ),
        ),
    ],
    ids=["optional_fields", "no_optional_fields"],
)
def test_batch__to_json(contents, expected):
    b = batch.Batch(**contents)

    assert b.to_json() == expected


def test_batch_membership__direct_create(create_batch_db, db_session, test_batches):
    b = test_batches[0]
    db_session.add(
        batch.BatchMembership(batch_id=b.id, node_id="node_1", node_type="rma")
    )
    db_session.commit()

    bm = (
        db_session.query(batch.BatchMembership)
        .filter(batch.BatchMembership.batch_id == b.id)
        .one()
    )

    assert bm.node_id == "node_1"
    assert bm.node_type == "rma"
    assert len(b.members) == 1
    assert bm == b.members[0]


def test_batch_membership__indirect_create(create_batch_db, db_session, test_batches):
    b = test_batches[0]
    b.members.append(batch.BatchMembership(node_id="node_1", node_type="rma"))
    db_session.commit()

    bm = (
        db_session.query(batch.BatchMembership)
        .filter(batch.BatchMembership.batch_id == b.id)
        .one()
    )

    assert bm.node_id == "node_1"
    assert bm.node_type == "rma"
    assert len(b.members) == 1
    assert bm == b.members[0]


def test_batch_membership__primary_key_constraint(
    create_batch_db, db_session, test_batches
):
    b = test_batches[0]
    db_session.add(
        batch.BatchMembership(batch_id=b.id, node_id="node_1", node_type="rma")
    )
    db_session.commit()
    with pytest.raises(exc.IntegrityError, match=r"batch_membership_pk"):
        db_session.add(
            batch.BatchMembership(batch_id=b.id, node_id="node_1", node_type="sur")
        )
        db_session.commit()


def test_batch_membership__foreign_key_constraint(create_batch_db, db_session):
    with pytest.raises(exc.IntegrityError, match=r"batch_membership_batch_id_fk"):
        db_session.add(
            batch.BatchMembership(batch_id=1, node_id="node_1", node_type="sur")
        )
        db_session.commit()


@pytest.mark.parametrize(
    "contents",
    [{"node_type": "rma"}, {"node_id": "node_1"}],
    ids=["node_id_is_required", "node_type_is_required"],
)
def test_batch_membership__required_fields(
    create_batch_db, db_session, test_batches, contents
):
    b = test_batches[0]
    with pytest.raises(exc.IntegrityError, match="violates not-null constraint"):
        db_session.add(batch.BatchMembership(batch_id=b.id, **contents))
        db_session.commit()


def test_batch_membership__to_json():
    bm = batch.BatchMembership(batch_id=1, node_id="a", node_type="rma")
    expected = json.loads(
        json.dumps({"batch_id": 1, "node_id": "a", "node_type": "rma"})
    )
    assert bm.to_json() == expected


def test_batch_membership__node_in_multiple_batches(
    create_batch_db, db_session, test_batches
):
    b1 = test_batches[0]
    b2 = test_batches[1]

    b1.members.append(batch.BatchMembership(node_id="node_1", node_type="rma"))
    b2.members.append(batch.BatchMembership(node_id="node_1", node_type="rma"))
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

    assert b1.members[0] == bm1
    assert b2.members[0] == bm2


def test_batch_membership__delete_parent(
    create_batch_db, db_session, test_batches_with_members
):
    b1 = test_batches_with_members[0]
    b2 = test_batches_with_members[1]
    db_session.delete(b1)
    db_session.commit()

    assert db_session.query(batch.Batch).filter(batch.Batch.id == b1.id).first() == None
    assert_db_state_after_delete(db_session, b1, b2)


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
    assert_db_state_after_delete(db_session, b1, b2)


def test_batch_membership__delete_orphan(
    create_batch_db, db_session, test_batches_with_members
):
    b1 = test_batches_with_members[0]
    b2 = test_batches_with_members[1]
    b1.members.pop()
    b1.members.pop()
    db_session.commit()

    assert db_session.query(batch.Batch).filter(batch.Batch.id == b1.id).one() == b1
    assert_db_state_after_delete(db_session, b1, b2)