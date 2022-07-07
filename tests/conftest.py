# -*- coding: utf-8 -*-
"""
gdcdatamodel.test.conftest
----------------------------------

pytest setup for gdcdatamodel tests
"""
import pytest
import sqlalchemy
from sqlalchemy.orm import sessionmaker

from gdc_ng_models.models import (
    batch,
    cohort,
    download_reports,
    qcreport,
    redaction,
    released_data,
    studyrule,
)
from gdc_ng_models.snacks import database as db

Session = sessionmaker()


@pytest.fixture(scope="session")
def db_configs():
    return db.get_configs()


@pytest.fixture(scope="session")
def db_engine(db_configs):
    return db.postgres_engine_factory(db_configs)


@pytest.fixture(scope="session")
def create_reports_db(db_engine):
    download_reports.Base.metadata.create_all(db_engine)
    yield
    download_reports.Base.metadata.drop_all(db_engine)


@pytest.fixture(scope="session")
def create_qcreport_db(db_engine):
    qcreport.Base.metadata.create_all(db_engine)
    yield
    qcreport.Base.metadata.drop_all(db_engine)


@pytest.fixture(scope="session")
def create_redaction_log_db(db_engine):
    redaction.Base.metadata.create_all(db_engine)
    yield
    redaction.Base.metadata.drop_all(db_engine)


@pytest.fixture(scope="session")
def create_study_rule_db(db_engine):
    studyrule.Base.metadata.create_all(db_engine)
    yield
    studyrule.Base.metadata.drop_all(db_engine)


@pytest.fixture(scope="session")
def create_released_data_db(db_engine):
    released_data.Base.metadata.create_all(db_engine)
    yield
    released_data.Base.metadata.drop_all(db_engine)


@pytest.fixture(scope="session")
def create_batch_db(db_engine):
    batch.Base.metadata.create_all(db_engine)
    yield
    batch.Base.metadata.drop_all(db_engine)


@pytest.fixture(scope="session")
def create_cohort_db(db_engine):
    # type: (sqlalchemy.engine.base.Engine) -> None
    """Provides capabilities for setup and teardown of a test cohort database.

    This function relies on a side effect of yield to setup and teardown a
    cohort database for use with test cases. The function creates a cohort
    database on invocation and then pauses execution with a yield that returns
    no value but instead returns control to the calling function. Once the
    calling function exits, control is returned to this fixture and the
    database is dropped.
    """
    cohort.Base.metadata.create_all(db_engine)
    yield
    cohort.Base.metadata.drop_all(db_engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="module")
def db_module_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
