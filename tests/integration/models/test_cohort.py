import enum
import json
import uuid
import pytest
from gdc_ng_models.models import cohort
from sqlalchemy import exc


class CohortType(enum.Enum):
    static = 1
    dynamic = 2


@pytest.fixture(scope="function")
def fixture_context(create_cohort_db, db_session):
    """Create an anonymous context for use with test cases."""

    test_context = cohort.AnonymousContext()
    db_session.add(test_context)
    db_session.commit()
    return test_context


@pytest.fixture(scope="function")
def fixture_cohort(create_cohort_db, db_session, fixture_context):
    """Create a cohort for use with test cases."""

    test_cohort = cohort.Cohort(name="fixture_cohort", context_id=fixture_context.id)
    db_session.add(test_cohort)
    db_session.commit()
    return test_cohort


@pytest.fixture(scope="function")
def fixture_static_filter(create_cohort_db, db_session, fixture_cohort):
    """Create a static cohort filter for use with test cases."""

    test_filter = cohort.CohortFilter(
        cohort_id=fixture_cohort.id,
        filters=[
            {"field": "cases.primary_site", "value": ["breast", "bronchus and lung"]}
        ],
        cohort_type=CohortType.static.name,
    )
    db_session.add(test_filter)
    db_session.commit()
    return test_filter


@pytest.fixture(scope="function")
def fixture_static_filter_parent_child(create_cohort_db, db_session, fixture_cohort):
    """Create a static cohort filter hierarchy consisting of a parent and child."""

    # create parent
    parent_filter = cohort.CohortFilter(
        cohort_id=fixture_cohort.id,
        filters=[{"field": "cases.primary_site", "value": ["breast"]}],
        cohort_type=CohortType.static.name,
    )
    db_session.add(parent_filter)
    db_session.commit()

    # create child
    child_filter = cohort.CohortFilter(
        parent_id=parent_filter.id,
        cohort_id=fixture_cohort.id,
        filters=[{"field": "cases.primary_site", "value": ["bronchus and lung"]}],
        cohort_type=CohortType.static.name,
    )
    db_session.add(child_filter)
    db_session.commit()

    return parent_filter, child_filter


@pytest.fixture(scope="function")
def fixture_cohort_static_full(
    create_cohort_db, db_session, fixture_static_filter_parent_child
):
    """Create a static cohort with a full relationship hierarchy.

    This returns a static cohort with multiple filters, each including a snapshot
    """
    filter_1 = fixture_static_filter_parent_child[0]
    snapshot_1 = cohort.CohortSnapshot(
        filter_id=filter_1.id,
        data_release=uuid.uuid4(),
        case_ids=[uuid.uuid4() for i in range(10)],
    )
    db_session.add(snapshot_1)

    filter_2 = fixture_static_filter_parent_child[1]
    snapshot_2 = cohort.CohortSnapshot(
        filter_id=filter_2.id,
        data_release=uuid.uuid4(),
        case_ids=[uuid.uuid4() for i in range(10)],
    )
    db_session.add(snapshot_2)
    db_session.commit()

    return filter_1.cohort


def test_anonymous_context__valid_create(create_cohort_db, db_session):
    """Tests creation of a valid anonymous context entity."""

    # define expected values
    expected_id = uuid.uuid4()

    # create context
    test_context = cohort.AnonymousContext(id=expected_id)
    db_session.add(test_context)
    db_session.commit()

    # validate context
    assert test_context.id == expected_id


def test_anonymous_context__unique_ids(create_cohort_db, db_session):
    """Tests unique constraint on anonymous context ID."""

    target_id = uuid.uuid4()
    db_session.add(
        cohort.AnonymousContext(
            id=target_id,
        )
    )
    db_session.commit()

    with pytest.raises(
        exc.IntegrityError, match=r"violates unique constraint.*anonymous_context_pkey"
    ):
        db_session.add(
            cohort.AnonymousContext(
                id=target_id,
            )
        )
        db_session.commit()


def test_anonymous_context__defaults_unique_ids(create_cohort_db, db_session):
    """Tests default generated IDs on anonymous context are unique."""

    context_1 = cohort.AnonymousContext()
    context_2 = cohort.AnonymousContext()
    db_session.add_all([context_1, context_2])
    db_session.commit()

    assert context_1.id is not None
    assert context_2.id is not None
    assert context_1.id != context_2.id


def test_anonymous_context__to_json(create_cohort_db, db_session):
    """Tests json output for anonymous context is valid."""

    test_context = cohort.AnonymousContext()
    db_session.add(test_context)
    db_session.commit()

    expected_json = json.loads(
        json.dumps(
            {
                "id": str(test_context.id),
                "created_datetime": test_context.created_datetime.isoformat(),
                "updated_datetime": test_context.updated_datetime.isoformat(),
            }
        )
    )

    assert test_context.to_json() == expected_json


def test_cohort__valid_create(create_cohort_db, db_session, fixture_context):
    """Tests creation of a valid cohort entity."""

    # define expected values
    expected_id = uuid.uuid4()
    expected_name = "test_cohort"
    expected_context_id = fixture_context.id

    # create cohort
    test_cohort = cohort.Cohort(
        id=expected_id,
        name=expected_name,
        context_id=expected_context_id,
    )
    db_session.add(test_cohort)
    db_session.commit()

    # validate cohort
    assert test_cohort.id == expected_id
    assert test_cohort.name == expected_name
    assert test_cohort.context_id == expected_context_id


def test_cohort__unique_ids(create_cohort_db, db_session, fixture_context):
    """Tests unique constraint on cohort ID."""

    target_id = uuid.uuid4()
    db_session.add(
        cohort.Cohort(
            id=target_id,
            name="test_cohort_1",
            context_id=fixture_context.id,
        )
    )
    db_session.commit()

    with pytest.raises(
        exc.IntegrityError, match=r"violates unique constraint.*cohort_pkey"
    ):
        db_session.add(
            cohort.Cohort(
                id=target_id,
                name="test_cohort_2",
                context_id=fixture_context.id,
            )
        )
        db_session.commit()


def test_cohort__defaults_unique_ids(create_cohort_db, db_session, fixture_context):
    """Tests default generated IDs on cohort are unique."""

    cohort_1 = cohort.Cohort(name="cohort_1", context_id=fixture_context.id)
    cohort_2 = cohort.Cohort(name="cohort_2", context_id=fixture_context.id)
    db_session.add(cohort_1)
    db_session.add(cohort_2)
    db_session.commit()

    assert cohort_1.id is not None
    assert cohort_2.id is not None
    assert cohort_1.id != cohort_2.id


def test_cohort__anonymous_context_bidirectional_relationship(
    create_cohort_db, db_session, fixture_context
):
    """Tests bidirectional relationship between cohort and anonymous context."""

    test_cohort = cohort.Cohort(name="test_cohort", context_id=fixture_context.id)
    db_session.add(test_cohort)
    db_session.commit()

    assert test_cohort.context == fixture_context
    assert test_cohort in fixture_context.cohorts


def test_cohort__current_filter(create_cohort_db, db_session, fixture_cohort):
    """Tests the current filter function is retrieving the latest filter."""

    # create first filter and validate returned as current
    filter_1 = cohort.CohortFilter(
        parent_id=None,
        cohort_id=fixture_cohort.id,
        filters=[],
        cohort_type=CohortType.dynamic.name,
    )
    db_session.add(filter_1)
    db_session.commit()
    assert fixture_cohort.get_current_filter() == filter_1

    # create second filter and validate returned as current
    filter_2 = cohort.CohortFilter(
        parent_id=filter_1.id,
        cohort_id=fixture_cohort.id,
        filters=[],
        cohort_type=CohortType.dynamic.name,
    )
    db_session.add(filter_2)
    db_session.commit()
    assert filter_1 != filter_2
    assert fixture_cohort.get_current_filter() == filter_2


def test_cohort__context_fkey_constraint(create_cohort_db, db_session):
    """Tests cohort foreign key constraint on context_id."""

    non_existent_id = uuid.uuid4()
    with pytest.raises(exc.IntegrityError, match=r"violates foreign key constraint"):
        db_session.add(
            cohort.Cohort(
                name="test_cohort_1",
                context_id=non_existent_id,
            )
        )
        db_session.commit()


def test_cohort__name_not_nullable(create_cohort_db, db_session, fixture_context):
    """Tests name must be defined for cohort."""

    with pytest.raises(exc.IntegrityError, match=r"violates not-null constraint"):
        db_session.add(
            cohort.Cohort(
                id=uuid.uuid4(),
                context_id=fixture_context.id,
            )
        )
        db_session.commit()


def test_cohort__to_json(create_cohort_db, db_session, fixture_context):
    """Tests json output for cohort is valid."""

    test_cohort = cohort.Cohort(
        name="test_cohort",
        id=uuid.uuid4(),
        context_id=fixture_context.id,
    )
    db_session.add(test_cohort)
    db_session.commit()

    expected_json = json.loads(
        json.dumps(
            {
                "id": str(test_cohort.id),
                "name": test_cohort.name,
                "context_id": str(test_cohort.context_id),
                "created_datetime": test_cohort.created_datetime.isoformat(),
                "updated_datetime": test_cohort.updated_datetime.isoformat(),
            }
        )
    )

    assert test_cohort.to_json() == expected_json


def test_cohort_filter__valid_create(create_cohort_db, db_session, fixture_cohort):
    """Tests creation of a valid cohort filter entity."""

    # define expected values
    expected_id = 1
    expected_cohort_id = fixture_cohort.id
    expected_filters = [
        {"field": "cases.primary_site", "value": ["breast", "bronchus and lung"]}
    ]
    expected_type = CohortType.static.name

    # create cohort filter
    test_filter = cohort.CohortFilter(
        id=expected_id,
        parent_id=None,
        cohort_id=expected_cohort_id,
        filters=expected_filters,
        cohort_type=expected_type,
    )
    db_session.add(test_filter)
    db_session.commit()

    # validate cohort filter
    assert test_filter.id == expected_id
    assert test_filter.parent_id is None
    assert test_filter.cohort_id == expected_cohort_id
    assert test_filter.filters == expected_filters
    assert test_filter.cohort_type == expected_type


def test_cohort_filter__unique_ids(create_cohort_db, db_session, fixture_cohort):
    """Tests unique constraint on cohort filter ID."""

    target_id = 1
    db_session.add(
        cohort.CohortFilter(
            id=target_id,
            cohort_id=fixture_cohort.id,
            filters=[],
        )
    )
    db_session.commit()

    with pytest.raises(
        exc.IntegrityError, match=r"violates unique constraint.*cohort_filter_pkey"
    ):
        db_session.add(
            cohort.CohortFilter(
                id=target_id,
                cohort_id=fixture_cohort.id,
                filters=[],
            )
        )
        db_session.commit()


def test_cohort_filter__defaults_unique_ids(
    create_cohort_db, db_session, fixture_cohort
):
    """Tests default generated IDs on cohort filter are unique."""

    filter_1 = cohort.CohortFilter(cohort_id=fixture_cohort.id, filters=[])
    filter_2 = cohort.CohortFilter(cohort_id=fixture_cohort.id, filters=[])
    db_session.add_all([filter_1, filter_2])
    db_session.commit()

    assert filter_1.id is not None
    assert filter_2.id is not None
    assert filter_1.id != filter_2.id


def test_cohort_filter__cohort_bidirectional_relationship(
    create_cohort_db, db_session, fixture_cohort
):
    """Tests bidirectional relationship between cohort filter and cohort."""

    test_filter = cohort.CohortFilter(
        parent_id=None,
        cohort_id=fixture_cohort.id,
        filters=[],
        cohort_type=CohortType.dynamic.name,
    )
    db_session.add(test_filter)
    db_session.commit()

    assert test_filter.cohort == fixture_cohort
    assert test_filter in fixture_cohort.filters


def test_cohort_filter__cohort_fkey_constraint(create_cohort_db, db_session):
    """Tests cohort filter foreign key constraint on cohort_id."""

    non_existent_id = uuid.uuid4()
    with pytest.raises(exc.IntegrityError, match=r"violates foreign key constraint"):
        db_session.add(
            cohort.CohortFilter(
                cohort_id=non_existent_id,
                filters=[],
            )
        )
        db_session.commit()


def test_cohort_filter__filters_not_nullable(
    create_cohort_db, db_session, fixture_cohort
):
    """Tests filters must be defined for cohort filter."""

    with pytest.raises(exc.IntegrityError, match=r"violates not-null constraint"):
        db_session.add(
            cohort.CohortFilter(
                cohort_id=fixture_cohort.id,
            )
        )
        db_session.commit()


def test_cohort_filter__static_default(create_cohort_db, db_session, fixture_cohort):
    """Tests static indicator on cohort filter defaults to false."""

    test_filter = cohort.CohortFilter(cohort_id=fixture_cohort.id, filters=[])
    db_session.add(test_filter)
    db_session.commit()

    assert test_filter.cohort_type == CohortType.static.name


def test_cohort_filter__parent_id_history(create_cohort_db, db_session, fixture_cohort):
    """Tests history is maintained via parent_id on cohort filter."""

    # create parent filter
    parent_filter = cohort.CohortFilter(
        cohort_id=fixture_cohort.id,
        filters=[{"field": "cases.primary_site", "value": ["breast"]}],
    )
    db_session.add(parent_filter)
    db_session.commit()

    # create first child filter
    child_filter_1 = cohort.CohortFilter(
        parent_id=parent_filter.id,
        cohort_id=fixture_cohort.id,
        filters=[{"field": "cases.primary_site", "value": ["bronchus and lung"]}],
    )
    db_session.add(child_filter_1)
    db_session.commit()

    # create second child filter
    child_filter_2 = cohort.CohortFilter(
        parent_id=child_filter_1.id,
        cohort_id=fixture_cohort.id,
        filters=[{"field": "cases.primary_site", "value": ["colon"]}],
    )
    db_session.add(child_filter_2)
    db_session.commit()

    assert parent_filter.parent_id is None
    assert child_filter_1.parent_id == parent_filter.id
    assert child_filter_2.parent_id == child_filter_1.id


def test_cohort_filter__to_json(create_cohort_db, db_session, fixture_cohort):
    """Tests json output for cohort filter is valid."""

    test_filter = cohort.CohortFilter(
        cohort_id=fixture_cohort.id,
        filters=[
            {"field": "cases.primary_site", "value": ["breast", "bronchus and lung"]}
        ],
    )
    db_session.add(test_filter)
    db_session.commit()

    expected_json = json.loads(
        json.dumps(
            {
                "id": test_filter.id,
                "parent_id": None,
                "cohort_id": str(test_filter.cohort_id),
                "filters": test_filter.filters,
                "cohort_type": test_filter.cohort_type,
                "created_datetime": test_filter.created_datetime.isoformat(),
                "updated_datetime": test_filter.updated_datetime.isoformat(),
            }
        )
    )

    assert test_filter.to_json() == expected_json


def test_cohort_snapshot__valid_create(
    create_cohort_db, db_session, fixture_static_filter
):
    """Tests creation of a valid cohort snapshot entity."""

    # define expected values
    expected_id = 1
    expected_filter_id = fixture_static_filter.id
    expected_data_release = uuid.uuid4()
    expected_case_ids = [uuid.uuid4() for i in range(10)]

    # create snapshot
    test_snapshot = cohort.CohortSnapshot(
        id=expected_id,
        filter_id=expected_filter_id,
        data_release=expected_data_release,
        case_ids=expected_case_ids,
    )
    db_session.add(test_snapshot)
    db_session.commit()

    # validate snapshot
    assert test_snapshot.id == expected_id
    assert test_snapshot.filter_id == expected_filter_id
    assert test_snapshot.data_release == expected_data_release
    assert test_snapshot.case_ids == expected_case_ids


def test_cohort_snapshot__unique_ids(
    create_cohort_db, db_session, fixture_static_filter_parent_child
):
    """Tests unique constraint on cohort snapshot ID."""

    target_id = 1

    # due to unique constraint, each snapshot must have a unique filter
    filter_1 = fixture_static_filter_parent_child[0]
    filter_2 = fixture_static_filter_parent_child[1]

    # create snapshot
    db_session.add(
        cohort.CohortSnapshot(
            id=target_id,
            filter_id=filter_1.id,
            data_release=uuid.uuid4(),
            case_ids=[uuid.uuid4() for i in range(10)],
        )
    )
    db_session.commit()

    # attempt to create a second snapshot with duplicate ID
    with pytest.raises(
        exc.IntegrityError, match=r"violates unique constraint.*cohort_snapshot_pkey"
    ):
        db_session.add(
            cohort.CohortSnapshot(
                id=target_id,
                filter_id=filter_2.id,
                data_release=uuid.uuid4(),
                case_ids=[uuid.uuid4() for i in range(10)],
            )
        )
        db_session.commit()


def test_cohort_snapshot__default_unique_ids(
    create_cohort_db, db_session, fixture_static_filter_parent_child
):
    """Tests default generated IDs on cohort snapshot are unique."""

    # due to unique constraint, each snapshot must have a unique filter
    filter_1 = fixture_static_filter_parent_child[0]
    filter_2 = fixture_static_filter_parent_child[1]

    # create snapshots
    snapshot_1 = cohort.CohortSnapshot(
        filter_id=filter_1.id,
        data_release=uuid.uuid4(),
        case_ids=[uuid.uuid4() for i in range(10)],
    )
    snapshot_2 = cohort.CohortSnapshot(
        filter_id=filter_2.id,
        data_release=uuid.uuid4(),
        case_ids=[uuid.uuid4() for i in range(10)],
    )
    db_session.add_all([snapshot_1, snapshot_2])
    db_session.commit()

    assert snapshot_1.id is not None
    assert snapshot_2.id is not None
    assert snapshot_1.id != snapshot_2.id


def test_cohort_snapshot__cohort_filter_bidirectional_relationship(
    create_cohort_db, db_session, fixture_static_filter
):
    """Tests bidirectional relationship between cohort snapshot and cohort filter."""

    test_snapshot = cohort.CohortSnapshot(
        filter_id=fixture_static_filter.id,
        data_release=uuid.uuid4(),
        case_ids=[uuid.uuid4() for i in range(10)],
    )
    db_session.add(test_snapshot)
    db_session.commit()

    assert test_snapshot.filter == fixture_static_filter
    assert test_snapshot == fixture_static_filter.snapshot


def test_cohort_snapshot__cohort_filter_fkey_constraint(create_cohort_db, db_session):
    """Tests cohort snapshot foreign key constraint on cohort filter id."""

    non_existent_id = 12345

    with pytest.raises(exc.IntegrityError, match=r"violates foreign key constraint"):
        db_session.add(
            cohort.CohortSnapshot(
                filter_id=non_existent_id,
                data_release=uuid.uuid4(),
                case_ids=[uuid.uuid4() for i in range(10)],
            )
        )
        db_session.commit()


def test_cohort_snapshot__filter_id_unique_constraint(
    create_cohort_db, db_session, fixture_static_filter
):
    """Tests unique constraint on filter ID."""

    # create snapshot
    db_session.add(
        cohort.CohortSnapshot(
            filter_id=fixture_static_filter.id,
            data_release=uuid.uuid4(),
            case_ids=[uuid.uuid4() for i in range(10)],
        )
    )
    db_session.commit()

    # attempt to create a second snapshot using the same filter ID
    with pytest.raises(exc.IntegrityError, match=r"violates unique constraint"):
        db_session.add(
            cohort.CohortSnapshot(
                filter_id=fixture_static_filter.id,
                data_release=uuid.uuid4(),
                case_ids=[uuid.uuid4() for i in range(10)],
            )
        )
        db_session.commit()


def test_cohort_snapshot__data_release_not_nullable(
    create_cohort_db, db_session, fixture_static_filter
):
    """Tests data release must be defined for cohort snapshot."""

    with pytest.raises(exc.IntegrityError, match=r"violates not-null constraint"):
        db_session.add(
            cohort.CohortSnapshot(
                filter_id=fixture_static_filter.id,
                case_ids=[uuid.uuid4() for i in range(10)],
            )
        )
        db_session.commit()


def test_cohort_snapshot__case_ids_not_nullable(
    create_cohort_db, db_session, fixture_static_filter
):
    """Tests case IDs must be defined for cohort snapshot."""

    with pytest.raises(exc.IntegrityError, match=r"violates not-null constraint"):
        db_session.add(
            cohort.CohortSnapshot(
                filter_id=fixture_static_filter.id,
                data_release=uuid.uuid4(),
            )
        )
        db_session.commit()


def test_cohort_snapshot__to_json(create_cohort_db, db_session, fixture_static_filter):
    """Tests json output for cohort snapshot is valid."""

    test_snapshot = cohort.CohortSnapshot(
        id=1,
        filter_id=fixture_static_filter.id,
        data_release=uuid.uuid4(),
        case_ids=[uuid.uuid4() for i in range(10)],
    )
    db_session.add(test_snapshot)
    db_session.commit()

    expected_json = json.loads(
        json.dumps(
            {
                "id": test_snapshot.id,
                "filter_id": test_snapshot.filter_id,
                "data_release": str(test_snapshot.data_release),
                "case_ids": [str(case_id) for case_id in test_snapshot.case_ids],
                "created_datetime": test_snapshot.created_datetime.isoformat(),
                "updated_datetime": test_snapshot.updated_datetime.isoformat(),
            }
        )
    )

    assert test_snapshot.to_json() == expected_json


def test_cohort_cascade_delete(
    create_cohort_db,
    db_session,
    fixture_cohort_static_full,
):
    # record ids to delete
    test_cohort = fixture_cohort_static_full
    cohort_id = test_cohort.id
    filter_ids = [cohort_filter.id for cohort_filter in test_cohort.filters]
    snapshot_ids = [cohort_filter.snapshot.id for cohort_filter in test_cohort.filters]

    # validate test cohort details
    assert test_cohort is not None
    assert filter_ids is not None
    assert len(filter_ids) == 2
    assert len(snapshot_ids) == 2

    # validate database objects exist
    assert db_session.query(cohort.Cohort).get(cohort_id) is not None
    for filter_id in filter_ids:
        assert db_session.query(cohort.CohortFilter).get(filter_id) is not None
    for snapshot_id in snapshot_ids:
        assert db_session.query(cohort.CohortSnapshot).get(snapshot_id) is not None

    # delete cohort
    db_session.delete(test_cohort)
    db_session.commit()

    # verify cohort is deleted and cascades to related filters and snapshots
    assert db_session.query(cohort.Cohort).get(cohort_id) is None
    for filter_id in filter_ids:
        assert db_session.query(cohort.CohortFilter).get(filter_id) is None
    for snapshot_id in snapshot_ids:
        assert db_session.query(cohort.CohortSnapshot).get(snapshot_id) is None
