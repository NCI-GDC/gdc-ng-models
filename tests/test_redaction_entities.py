import pytest
import random
import uuid

from gdc_ng_models.models.redaction import (
    RedactionEntry,
    RedactionLog,
)


@pytest.fixture(scope="function")
def redacted_fixture(create_redaction_log_db, db_session):
    """ Creates a redacted log entry"""

    log = RedactionLog()
    log.initiated_by = "TEST"
    log.annotation_id = str(uuid.uuid4())
    log.project_id = "AB-BQ"
    log.reason = "Err"
    log.reason_category = "consent withdrawn"

    count = 0
    for i in range(random.randint(2, 5)):
        count += 1
        entry = RedactionEntry(node_id=str(uuid.uuid4()), node_type="Aligned Reads")
        log.entries.append(entry)

    db_session.add(log)
    db_session.commit()

    yield log.id, count


def test_log_redaction(redacted_fixture, db_session):

    sxn = db_session

    log_id, log_entries_count = redacted_fixture

    # query for just created nodes
    xlog = sxn.query(RedactionLog).get(log_id)
    assert xlog is not None
    assert len(xlog.entries) == log_entries_count


def test_all_rescind(redacted_fixture, db_session):

    sxn = db_session

    log_id, log_entries_count = redacted_fixture

    # rescind
    xlog = sxn.query(RedactionLog).get(log_id)
    xlog.rescind_all("TEST")
    sxn.commit()

    # verify
    xlog = sxn.query(RedactionLog).get(log_id)
    assert len(xlog.entries) == log_entries_count
    assert xlog.is_rescinded is True


def test_single_rescind(redacted_fixture, db_session):

    sxn = db_session

    log_id, log_entries_count = redacted_fixture

    # rescind
    xlog = sxn.query(RedactionLog).get(log_id)
    entry = xlog.entries[0]
    entry.rescind("TEST")
    rescinded_entry_id = entry.node_id
    sxn.commit()

    # verify
    xlog = sxn.query(RedactionLog).get(log_id)
    assert len(xlog.entries) == log_entries_count
    assert xlog.is_rescinded is False

    for entry in xlog.entries:
        if entry.node_id == rescinded_entry_id:
            assert entry.rescinded is True
        else:
            assert entry.rescinded is False
