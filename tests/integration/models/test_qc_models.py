import uuid

import pytest

from gdc_ng_models.models import qcreport


@pytest.fixture(scope="function")
def test_run(create_qcreport_db, db_session):
    # add
    tr = qcreport.TestRun(project_id="TEST-TEST")
    tr.entity_id = str(uuid.uuid4())
    tr.test_type = "aliquots"

    db_session.add(tr)
    db_session.commit()

    yield tr


def test_create_runs(create_qcreport_db, db_session):

    tr_id = str(uuid.uuid4())

    # add
    tr = qcreport.TestRun(project_id="TEST-TEST")
    tr.entity_id = tr_id
    tr.test_type = "aliquots"

    db_session.add(tr)
    db_session.commit()

    # verify
    trx = (
        db_session.query(qcreport.TestRun)
        .filter(qcreport.TestRun.entity_id == tr_id)
        .first()
    )

    assert trx.id == tr.id


def test_create_validation_result(test_run, db_session):

    vr = qcreport.ValidationResult()
    vr.id = 1
    vr.node_id = str(uuid.uuid4())
    vr.submitter_id = "some_submitter_id"
    vr.severity = "fatal"
    vr.error_type = "NO_READ_PAIR_NUMBER"
    vr.message = "The FASTQ is paired but has no read_pair_number"
    vr.node_type = "Submitted Aligned Read"

    tr = db_session.query(qcreport.TestRun).first()
    tr.test_results.append(vr)
    db_session.commit()

    # assert
    vr_list = (
        db_session.query(qcreport.ValidationResult)
        .filter(qcreport.ValidationResult.test_run == test_run)
        .all()
    )

    # single entry
    assert vr_list
    vr_1 = vr_list[0]
    assert vr.id == vr_1.id
    assert vr_1.severity == "CRITICAL"
