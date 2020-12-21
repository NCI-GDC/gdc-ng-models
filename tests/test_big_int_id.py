from copy import deepcopy
from sqlalchemy import inspect
from sqlalchemy.types import BIGINT

from gdc_ng_models.snacks import database as db
from gdc_ng_models.models import (
    misc,
    notifications,
    qcreport,
    redaction,
    released_data,
    reports,
    studyrule,
    submission,
)


TARGETED_TABLE_NAMES = [
    'filereport',
    'notifications',
    'qc_validation_results',
    'qc_test_runs',
    'redaction_log',
    "released_data_log",
    'gdc_reports',
    "study_rule",
    'transaction_logs',
    'transaction_documents',
]


def test_biginteger_id_column(db_configs):
    """Check the 'id' column of specific tables are BIGINT

    One assumption is that:
    for each of these tables, the `id` column is the primary_key and they are monotonically increasing

    some tables may have `id` in TEXT or other data_types which testing subjects here
    """
    new_configs = deepcopy(db_configs)
    new_configs["database"] = "big_int_test"
    engine = db.postgres_engine_factory(new_configs)

    misc.Base.metadata.create_all(engine)
    notifications.Base.metadata.create_all(engine)
    qcreport.Base.metadata.create_all(engine)
    redaction.Base.metadata.create_all(engine)
    released_data.Base.metadata.create_all(engine)
    reports.Base.metadata.create_all(engine)
    studyrule.Base.metadata.create_all(engine)
    submission.Base.metadata.create_all(engine)

    insp = inspect(engine)
    table_names = insp.get_table_names()
    table_columns_details = {}
    for table in table_names:
        table_columns_details[table] = {
            col['name']: col['type'] for col in insp.get_columns(table)
        }

    misc.Base.metadata.drop_all(engine)
    notifications.Base.metadata.drop_all(engine)
    qcreport.Base.metadata.drop_all(engine)
    redaction.Base.metadata.drop_all(engine)
    released_data.Base.metadata.drop_all(engine)
    reports.Base.metadata.drop_all(engine)
    studyrule.Base.metadata.drop_all(engine)
    submission.Base.metadata.drop_all(engine)

    for table in TARGETED_TABLE_NAMES:
        assert isinstance(table_columns_details[table]['id'], BIGINT)
