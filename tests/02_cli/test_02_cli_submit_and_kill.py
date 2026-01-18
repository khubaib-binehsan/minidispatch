from __future__ import annotations

from unittest.mock import patch
from minidispatch.main import app
from typer.testing import CliRunner
from minidispatch.db import manager as db_manager


def test_cli_submit_basic() -> None:
    runner = CliRunner()

    # Mock daemon to avoid starting it
    with patch("minidispatch.core.daemon.is_running", return_value=True):
        res = runner.invoke(
            app, ["submit", "* * * * *", "echo hello", "--name", "test-job"]
        )

    assert res.exit_code == 0
    assert "Job Submitted" in res.stdout
    assert "Successfully" in res.stdout
    assert "test-job" in res.stdout

    # Verify it's in the DB
    jobs = db_manager.get_jobs()
    assert len(jobs) == 1
    assert jobs[0]["name"] == "test-job"
    assert jobs[0]["command"] == "echo hello"
    assert jobs[0]["cron"] == "* * * * *"


def test_cli_submit_auto_name() -> None:
    runner = CliRunner()

    with patch("minidispatch.core.daemon.is_running", return_value=True):
        res = runner.invoke(app, ["submit", "0 0 * * *", "ls -la"])

    assert res.exit_code == 0
    assert "Job Submitted" in res.stdout
    assert "Successfully" in res.stdout

    jobs = db_manager.get_jobs()
    assert len(jobs) == 1
    assert jobs[0]["name"] is not None
    assert len(jobs[0]["name"]) > 0


def test_cli_submit_starts_daemon_if_not_running() -> None:
    runner = CliRunner()

    with (
        patch("minidispatch.core.daemon.is_running", return_value=False),
        patch("minidispatch.core.daemon.start") as mock_start,
    ):
        res = runner.invoke(app, ["submit", "1 2 3 4 5", "date"])

    assert res.exit_code == 0
    assert "Daemon not running, starting daemon..." in res.stdout
    mock_start.assert_called_once()


def test_cli_submit_duplicate_name_exits_1() -> None:
    runner = CliRunner()

    with patch("minidispatch.core.daemon.is_running", return_value=True):
        # First submission
        res1 = runner.invoke(
            app, ["submit", "* * * * *", "echo first", "--name", "duplicate"]
        )
        assert res1.exit_code == 0

        # Second submission with same name
        res2 = runner.invoke(
            app, ["submit", "0 * * * *", "echo second", "--name", "duplicate"]
        )
        assert res2.exit_code == 1
        assert "error submitting job" in res2.stdout.lower()


def test_cli_kill_basic() -> None:
    runner = CliRunner()

    # Currently kill just echos "Job details for: ..."
    res = runner.invoke(app, ["kill", "--job", "some-id"])

    assert res.exit_code == 0
    assert "Job details for: some-id" in res.stdout


def test_cli_kill_no_args_shows_help() -> None:
    runner = CliRunner()

    res = runner.invoke(app, ["kill"])

    assert res.exit_code == 0
    assert "Usage:" in res.stdout
    assert "Kill a specific run of a job" in res.stdout
