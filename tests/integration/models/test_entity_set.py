"""Tests for the entity_set module

Validations that need to be enforced programmatically as they
  do not raise an exception with sqlalchemy
  * EntitySet.id should not allow the empty string
  * EntitySet.entity_ids values cannot exceed 36 characters
  * EntitySet.entity_ids should be a unique 'set' not an array of values
"""
import json
import pytest
from gdc_ng_models.models import entity_set


STRING_36_CHAR = "00000000-0000-0000-0000-000000000000"
STRING_37_CHAR = "00000000-0000-0000-0000-0000000000001"
STRING_128_CHAR = "01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567"
STRING_129_CHAR = "012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678"


def create_nominal_entity_set() -> entity_set.EntitySet:
    """Helper to build a complete entity set to use for testing"""
    return entity_set.EntitySet(
        id=STRING_128_CHAR,
        type=entity_set.SetType.frozen,
        entity_type=entity_set.EntityType.case,
        entity_ids=[STRING_36_CHAR],
    )


def test_entity_set_create(create_entity_set_db, db_session):
    """Test Nominal path: create an entity_set"""
    objectUnderTest = create_nominal_entity_set()
    db_session.add(objectUnderTest)
    db_session.commit()

    assert objectUnderTest.id == STRING_128_CHAR
    assert objectUnderTest.type == entity_set.SetType.frozen
    assert objectUnderTest.entity_type == entity_set.EntityType.case
    assert objectUnderTest.entity_ids == [STRING_36_CHAR]
    assert objectUnderTest.accessed_datetime
    assert objectUnderTest.created_datetime
    assert objectUnderTest.updated_datetime


def test_entity_set_id_is_unique(create_entity_set_db, db_session):
    """Tests unique constraint on ID."""
    objectUnderTest = create_nominal_entity_set()
    db_session.add(objectUnderTest)
    db_session.commit()

    with pytest.raises(Exception):
        # duplicate entry
        db_session.add(create_nominal_entity_set())
        db_session.commit()


def test_entity_set_id_too_long(create_entity_set_db, db_session):
    """ID needs to support 64 CHARs but cannot exceed the limit of 128"""
    objectUnderTest = create_nominal_entity_set()
    objectUnderTest.id = STRING_129_CHAR
    with pytest.raises(Exception):
        db_session.add(objectUnderTest)
        db_session.commit()


def test_entity_set_id_cannot_be_none(create_entity_set_db, db_session):
    """ID cannot be None"""
    objectUnderTest = create_nominal_entity_set()
    objectUnderTest.id = None
    with pytest.raises(Exception):
        db_session.add(objectUnderTest)
        db_session.commit()


def test_entity_set_type_cannot_be_none(create_entity_set_db, db_session):
    """Confirm type cannot be None"""
    objectUnderTest = create_nominal_entity_set()
    objectUnderTest.type = None
    with pytest.raises(Exception):
        db_session.add(objectUnderTest)
        db_session.commit()


def test_entity_set_entity_type_cannot_be_none(create_entity_set_db, db_session):
    """Confirm entity_type cannot be None"""
    objectUnderTest = create_nominal_entity_set()
    objectUnderTest.entity_type = None
    with pytest.raises(Exception):
        db_session.add(objectUnderTest)
        db_session.commit()


def test_entity_set_entity_ids_cannot_be_none(create_entity_set_db, db_session):
    """Confirm entity_ids cannot be None"""
    objectUnderTest = create_nominal_entity_set()
    objectUnderTest.entity_ids = None
    with pytest.raises(Exception):
        db_session.add(objectUnderTest)
        db_session.commit()


def test_entity_set_to_json(create_entity_set_db, db_session):
    """Tests json output for entity_set is valid."""
    objectUnderTest = create_nominal_entity_set()
    db_session.add(objectUnderTest)
    db_session.commit()
    expected_json = json.loads(
        json.dumps(
            {
                "id": STRING_128_CHAR,
                "type": entity_set.SetType.frozen.name,
                "entity_type": entity_set.EntityType.case.name,
                "entity_ids": [STRING_36_CHAR],
                "created_datetime": objectUnderTest.created_datetime.isoformat(),
                "updated_datetime": objectUnderTest.updated_datetime.isoformat(),
                "accessed_datetime": objectUnderTest.accessed_datetime.isoformat(),
            }
        )
    )
    assert objectUnderTest.to_json() == expected_json
