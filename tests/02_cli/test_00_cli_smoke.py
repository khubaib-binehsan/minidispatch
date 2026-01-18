from __future__ import annotations

from minidispatch.main import app
from typer.testing import CliRunner


def test_cli_help() -> None:
    runner = CliRunner()

    res = runner.invoke(app, ["--help"])

    assert res.exit_code == 0
    assert "cronjob on steroids" in res.stdout


def test_cli_config_list() -> None:
    runner = CliRunner()

    res = runner.invoke(app, ["config", "list"])

    assert res.exit_code == 0
    assert "MINI_DISPATCH_DB" in res.stdout


def test_cli_config_get_unknown_key_exits_1() -> None:
    runner = CliRunner()

    res = runner.invoke(app, ["config", "get", "NOT_A_REAL_KEY"])

    assert res.exit_code == 1
    assert "not found" in res.stdout.lower()


def test_cli_config_get_real_key() -> None:
    runner = CliRunner()

    res = runner.invoke(app, ["config", "get", "MINI_DISPATCH_DB"])

    assert res.exit_code == 0
    assert "database.sqlite" in res.stdout
