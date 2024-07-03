from typing import Callable

import pytest
from sqlalchemy.engine import Engine


@pytest.mark.parametrize(
    "command", ["-h", "create --help", "grant --help", "revoke --help"]
)
def test_cli__sanity(ng_models_cli: Callable[[str], None], command: str) -> None:
    with pytest.raises(SystemExit) as v:
        ng_models_cli(command)
    assert v.value.code == 0


def test_cli__invalid_module(
    ng_models_cli: Callable[[str], None], db_args: str
) -> None:
    with pytest.raises(SystemExit) as v:
        ng_models_cli(f"-m skipper_tables {db_args} revoke -r ux -P read")
    assert v.value.code != 0


def test_cli__grant(
    db_engine: Engine, ng_models_cli: Callable[[str], None], db_args: str
) -> None:
    stmt = "drop role if exists resty; create user resty with password 'password';"
    conn = db_engine.connect()
    conn.execute(stmt)
    conn.close()

    ng_models_cli(f"-m redaction {db_args} create")
    ng_models_cli(f"-m redaction {db_args} grant -r restr -P read")

    # revoke
    ng_models_cli(f"-m redaction {db_args} revoke -r restr -P read")
