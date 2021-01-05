import pytest

from gdc_ng_models.models import notifications, released_data


@pytest.mark.usefixtures("create_released_data_db")
def test_big_int_id(db_session):
    large_int = 1234567890123456

    rdl_node = released_data.ReleasedDataLog(
        id=large_int,
        program_name="DummyProgram",
        project_code="DummyProject",
        release_number="dummy",
        data_type="cnv",
        is_open=True,
        action="release"
    )
    db_session.add(rdl_node)
    db_session.commit()
    node = db_session.query(released_data.ReleasedDataLog).first()
    assert node.id == large_int
