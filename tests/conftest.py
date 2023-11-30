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
    entity_set,
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
def create_entity_set_db(db_engine):
    # type: (sqlalchemy.engine.base.Engine) -> None
    """Provides capabilities for setup and teardown of a test entity_sets tables.

    Creates tables in a database using the declarations in the entity_set module in the
    gdc_ng_models/models package. This includes the following tables:
        entity_set: Contains the persistent set records

    Args:
        db_engine: A sqlalchemy database engine.

    Yields:
        None.
    """
    entity_set.Base.metadata.create_all(db_engine)
    yield
    entity_set.Base.metadata.drop_all(db_engine)


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

    Creates a database using the declarations in the cohort module in the
    gdc_ng_models/models package. This includes the following tables:
        anonymous_context: Used to authorize changes to a cohort.
        cohort: Defines the basic properties (name, id, context) of a cohort.
        cohort_filter: Defines the filter used to generate a cohort case set.
        cohort_snapshot: Defines the set of cases for a static cohort.

    Args:
        db_engine: A sqlalchemy database engine.

    Yields:
        None.
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
