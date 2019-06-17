# -*- coding: utf-8 -*-
"""
gdcdatamodel.test.conftest
----------------------------------

pytest setup for gdcdatamodel tests
"""
from sqlalchemy.orm import sessionmaker
import random
import uuid

from gdc_ng_models import models
from gdc_ng_models.snacks import database as db
#from psqlgraph import PsqlGraphDriver

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
    models.download_reports.Base.metadata.create_all(db_engine)
    yield
    models.download_reports.Base.metadata.drop_all(db_engine)


@pytest.fixture(scope='function')
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


#@pytest.fixture(scope='session')
#def db_config():
#    return {
#        'host': 'localhost',
#        'user': 'test',
#        'password': 'test',
#        'database': 'automated_test',
#    }
#
#
#@pytest.fixture(scope='session')
#def pg_driver_reports(request, db_config):
#
#    pg_driver = PsqlGraphDriver(**db_config)
#
#    def teardown():
#        for table in reversed(
#                models.download_reports.Base.metadata.sorted_tables):
#            table.drop(pg_driver.engine, checkfirst=True)
#
#    # ensure clean db
#    teardown()
#
#    models.download_reports.Base.metadata.create_all(pg_driver.engine)
#
#    request.addfinalizer(teardown)
#    return pg_driver
#
#
#@pytest.fixture(scope='session')
#def g(db_config):
#    """Fixture for database driver"""
#
#    return PsqlGraphDriver(**db_config)
#
#
#@pytest.fixture()
#def redacted_fixture(g):
#    """ Creates a redacted log entry"""
#
#    with g.session_scope() as sxn:
#        log = models.redaction.RedactionLog()
#        log.initiated_by = "TEST"
#        log.annotation_id = str(uuid.uuid4())
#        log.project_id = "AB-BQ"
#        log.reason = "Err"
#        log.reason_category = "consent withdrawn"
#
#        count = 0
#        for i in range(random.randint(2, 5)):
#            count += 1
#            entry = models.redaction.RedactionEntry(node_id=str(uuid.uuid4()), node_type="Aligned Reads")
#            log.entries.append(entry)
#
#        sxn.add(log)
#        sxn.commit()
#    yield log.id, count
#
#    # clean up
#    with g.session_scope() as sxn:
#        log = sxn.query(models.redaction.RedactionLog).get(log.id)
#        # remove all entries
#        for entry in log.entries:
#            sxn.delete(entry)
#        sxn.delete(log)
