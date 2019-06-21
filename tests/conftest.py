# -*- coding: utf-8 -*-
"""
gdcdatamodel.test.conftest
----------------------------------

pytest setup for gdcdatamodel tests
"""
from sqlalchemy.orm import sessionmaker

from gdc_ng_models.models import (
    download_reports,
    qcreport,
    redaction,
)
from gdc_ng_models.snacks import database as db

import pytest


Session = sessionmaker()


@pytest.fixture(scope='session')
def db_configs():
    return db.get_configs()


@pytest.fixture(scope='session')
def db_engine(db_configs):
    return db.postgres_engine_factory(db_configs)


@pytest.fixture(scope='session')
def create_reports_db(db_engine):
    download_reports.Base.metadata.create_all(db_engine)
    yield
    download_reports.Base.metadata.drop_all(db_engine)


@pytest.fixture(scope='session')
def create_qcreport_db(db_engine):
    qcreport.Base.metadata.create_all(db_engine)
    yield
    qcreport.Base.metadata.drop_all(db_engine)


@pytest.fixture(scope='session')
def create_redaction_log_db(db_engine):
    redaction.Base.metadata.create_all(db_engine)
    yield
    redaction.Base.metadata.drop_all(db_engine)


@pytest.fixture(scope='function')
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope='module')
def db_module_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
