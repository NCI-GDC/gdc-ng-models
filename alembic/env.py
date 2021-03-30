from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

import gdc_ng_models.models.batch as batch_models
import gdc_ng_models.models.download_reports as download_reports_models
import gdc_ng_models.models.misc as misc_models
import gdc_ng_models.models.notifications as notifications_models
import gdc_ng_models.models.qcreport as qcreport_models
import gdc_ng_models.models.redaction as redaction_models
import gdc_ng_models.models.released_data as released_data_models
import gdc_ng_models.models.reports as reports_models
import gdc_ng_models.models.studyrule as studyrule_models
import gdc_ng_models.models.submission as submission_models


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

target_metadata = [
    batch_models.Base.metadata,
    download_reports_models.Base.metadata,
    misc_models.Base.metadata,
    notifications_models.Base.metadata,
    qcreport_models.Base.metadata,
    redaction_models.Base.metadata,
    released_data_models.Base.metadata,
    reports_models.Base.metadata,
    studyrule_models.Base.metadata,
    submission_models.Base.metadata,
]

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.
    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()