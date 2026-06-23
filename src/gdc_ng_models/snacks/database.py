import os
from logging import getLogger

from sqlalchemy import create_engine

from gdc_ng_models.utils.decorators import try_or_log_error

logger = getLogger(__name__)

PERMISSIONS = dict(READ="SELECT", WRITE="SELECT, INSERT, UPDATE, DELETE")


def get_configs():
    return {
        "host": os.environ["PG_HOST"],
        "database": os.environ["PG_NAME"],
        "admin_user": os.environ["PG_USER"],
        "admin_password": os.environ["PG_PASS"],
    }


def postgres_engine_factory(configs):
    return create_engine(
        "postgresql://{user}:{password}@{host}/{database}".format(
            user=configs.get("admin_user"),
            password=configs.get("admin_password"),
            host=configs.get("host"),
            database=configs.get("database"),
        )
    )


def postgres_conn_factory(configs):
    engine = postgres_engine_factory(configs)
    conn = engine.connect()
    return conn


def execute_statement(configs, stmt, success):
    conn = postgres_conn_factory(configs)
    conn.execute("commit")
    conn.execute(stmt)
    conn.close()
    logger.info(success)


@try_or_log_error(logger)
def drop_database(configs, database):
    stmt = f"drop database {database}"
    execute_statement(configs, stmt, drop_database.__name__ + " success")


@try_or_log_error(logger)
def create_database(configs, database):
    stmt = f"create database {database}"
    execute_statement(configs, stmt, create_database.__name__ + " success")


@try_or_log_error(logger)
def drop_user(configs, user):
    stmt = f"drop user {user}"
    execute_statement(configs, stmt, drop_user.__name__ + " success")


@try_or_log_error(logger)
def create_user(configs, user, password):
    stmt = f"create user {user} with password '{password}'"
    execute_statement(configs, stmt, create_user.__name__ + " success")


@try_or_log_error(logger)
def grant_all_privileges(configs, database, user):
    stmt = f"grant all privileges on database {database} to {user}"
    execute_statement(configs, stmt, grant_all_privileges.__name__ + " success")


@try_or_log_error(logger)
def grant_privilege(configs: dict, permission: str, user: str, tables: list[str]) -> None:
    """Grants the given users the given permission for all the given tables."""
    stmt = "GRANT {permission} ON {tables} TO {user}".format(
        tables=", ".join(tables), permission=PERMISSIONS[permission.upper()], user=user
    )
    logger.debug(stmt)
    execute_statement(configs, stmt, grant_privilege.__name__ + " success")


@try_or_log_error(logger)
def revoke_privilege(configs, permission, user, tables):

    stmt = "REVOKE {permission} ON {tables} FROM {user}".format(
        tables=", ".join(tables), permission=PERMISSIONS[permission.upper()], user=user
    )
    logger.debug(stmt)
    execute_statement(configs, stmt, revoke_privilege.__name__ + " success")
