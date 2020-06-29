import pytest
from sqlalchemy.sql.expression import func

from gdc_ng_models.models import released_data


@pytest.fixture
def fake_released_data(create_released_data_db, db_session):
    def helper(
        name="name", code="code", is_controlled=False, data_type="cnv", is_open=False,
    ):
        node = released_data.ReleasedData(
            program_name=name,
            project_code=code,
            is_controlled=is_controlled,
            data_type=data_type,
            is_open=is_open,
        )

        db_session.merge(node)
        return node

    return helper


@pytest.fixture
def fake_released_log(create_released_data_db, db_session, request):
    def helper(
        name="name",
        code="code",
        release_number="1",
        data_type="cnv",
        is_open=False,
        action="release",
    ):
        node = released_data.ReleasedDataLog(
            program_name=name,
            project_code=code,
            release_number=release_number,
            data_type=data_type,
            is_open=is_open,
            action=action,
        )
        db_session.merge(node)
        return node

    return helper


def test_released_data__sqlalchemy_model_registered():
    assert released_data.ReleasedData


@pytest.mark.parametrize("data_type", ["cnv", "ssm", "case"])
def test_released_data__valid_data_type(fake_released_data, db_session, data_type):
    fake_released_data(data_type=data_type)
    node = db_session.query(released_data.ReleasedData).first()

    assert node.data_type == data_type
    db_session.delete(node)


def test_released_data__invalid_data_type(fake_released_data):
    with pytest.raises(ValueError, match=r"not a valid value for data_type"):
        fake_released_data(data_type="not-applicable")


def test_released_data__project_id(fake_released_data, db_session):
    fake_released_data()
    node = db_session.query(released_data.ReleasedData).first()
    assert node.project_id == "{}-{}".format(node.program_name, node.project_code)


def test_released_data__id(fake_released_data, db_session):
    fake_released_data()
    node = db_session.query(released_data.ReleasedData).first()
    assert node.id == "name_code_cnv", "id for ReleasedData is not correct."


def test_release_data_log__sqlalchemy_model_registered():
    assert released_data.ReleasedDataLog


@pytest.mark.parametrize("data_type", ["cnv", "ssm", "case"])
def test_release_data_log__valid_data_type(db_session, data_type, fake_released_log):
    fake_released_log(data_type=data_type)
    db_session.commit()
    node = db_session.query(released_data.ReleasedDataLog).first()

    assert node.data_type == data_type


def test_release_data_log__invalid_data_type(db_session, fake_released_log):
    with pytest.raises(ValueError, match=r"not a valid value for data_type"):
        fake_released_log(data_type="not-applicable")


@pytest.mark.parametrize("action", ["release", "unrelease"])
def test_release_data_log__valid_action(db_session, action, fake_released_log):
    fake_released_log(action=action)
    db_session.commit()
    node = db_session.query(released_data.ReleasedDataLog).first()

    assert node.action == action


def test_release_data_log__invalid_action(db_session, fake_released_log):
    with pytest.raises(ValueError, match=r"not a valid value for action"):
        fake_released_log(action="not-applicable")


def test_release_data_log__auto_increment(db_session, fake_released_log):
    max_id = -1
    for i in range(10):
        fake_released_log(release_number=str(i))
        current_id = db_session.query(
            func.max(released_data.ReleasedDataLog.id)
        ).scalar()
        assert current_id > max_id
        max_id = current_id


def test_release_data_log__project_id(fake_released_log, db_session):
    fake_released_log()
    node = db_session.query(released_data.ReleasedDataLog).first()
    assert node.project_id == "{}-{}".format(node.program_name, node.project_code)
