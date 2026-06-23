"""gdcdatamodel.test.conftest
----------------------------------

pytest setup for gdcdatamodel tests
"""

import shlex
from collections.abc import Callable, Iterator

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from gdc_ng_models import cli
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
def db_args(db_configs: dict[str, str]) -> str:
    return (
        f"-H {db_configs['host']} -d {db_configs['database']} -u {db_configs['admin_user']} "
        f"-p {db_configs['admin_password']}"
    )


@pytest.fixture(scope="session")
def db_engine(db_configs: dict[str, str]) -> Engine:
    return db.postgres_engine_factory(db_configs)


@pytest.fixture(scope="session")
def create_reports_db(db_engine, ng_models_cli, db_args: str) -> None:
    ng_models_cli(f"-m download_reports {db_args} create")
    yield
    download_reports.Base.metadata.drop_all(db_engine)


@pytest.fixture(scope="session")
def create_entity_set_db(
    db_engine: Engine, db_args: str, ng_models_cli: Callable[[str], None]
) -> Iterator[None]:
    """Provides capabilities for setup and teardown of a test entity_sets tables.

    Creates tables in a database using the declarations in the entity_set module in the
    gdc_ng_models/models package. This includes the following tables:
        entity_set: Contains the persistent set records

    Args:
        db_engine: A sqlalchemy database engine.
        db_args:
        ng_models_cli

    Yields:
        None.
    """
    ng_models_cli(f"-m entity_set {db_args} create")
    yield
    entity_set.Base.metadata.drop_all(db_engine)


@pytest.fixture(scope="session")
def create_qcreport_db(db_engine: Engine, db_args: str, ng_models_cli: Callable[[str], None]):
    ng_models_cli(f"-m qcreport {db_args} create")
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


@pytest.fixture(scope="session")
def ng_models_cli() -> Callable[[str], None]:
    def runner(command: str) -> None:
        cli.main(shlex.split(command))

    return runner
