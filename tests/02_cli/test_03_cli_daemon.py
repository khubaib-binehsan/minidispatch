from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from minidispatch.main import app
from typer.testing import CliRunner


def test_cli_daemon_status() -> None:
    runner = CliRunner()

    with patch("minidispatch.core.daemon.get_status", return_value="Daemon is running"):
        res = runner.invoke(app, ["daemon", "status"])

    assert res.exit_code == 0
    assert "Daemon is running" in res.stdout


def test_cli_daemon_stop_when_running() -> None:
    runner = CliRunner()

    with (
        patch("minidispatch.core.daemon.is_running", return_value=True),
        patch(
            "minidispatch.core.daemon.stop", return_value="Daemon stopped"
        ) as mock_stop,
    ):
        res = runner.invoke(app, ["daemon", "stop"])

    assert res.exit_code == 0
    assert "Daemon stopped" in res.stdout
    mock_stop.assert_called_once()


def test_cli_daemon_stop_when_not_running() -> None:
    runner = CliRunner()

    with patch("minidispatch.core.daemon.is_running", return_value=False):
        res = runner.invoke(app, ["daemon", "stop"])

    assert res.exit_code == 0
    assert "Daemon is not running" in res.stdout


def test_cli_daemon_start_already_running() -> None:
    runner = CliRunner()

    with (
        patch("minidispatch.core.daemon.is_running", return_value=True),
        patch("minidispatch.core.daemon.get_status", return_value="Already running"),
    ):
        res = runner.invoke(app, ["daemon", "start"])

    assert res.exit_code == 0
    assert "Already running" in res.stdout


def test_cli_daemon_start_not_running() -> None:
    runner = CliRunner()

    with (
        patch("minidispatch.core.daemon.is_running", return_value=False),
        patch("minidispatch.core.daemon.start") as mock_start,
        patch("minidispatch.core.daemon.get_status", return_value="Daemon started"),
    ):
        res = runner.invoke(app, ["daemon", "start"])

    assert res.exit_code == 0
    assert "Starting daemon..." in res.stdout
    assert "Daemon started" in res.stdout
    mock_start.assert_called_once()


def test_cli_daemon_restart() -> None:
    runner = CliRunner()

    with (
        patch("minidispatch.core.daemon.stop") as mock_stop,
        patch("minidispatch.core.daemon.start") as mock_start,
        patch("minidispatch.core.daemon.get_status", return_value="Daemon status"),
    ):
        res = runner.invoke(app, ["daemon", "restart"])

    assert res.exit_code == 0
    assert "Restarting daemon..." in res.stdout
    mock_stop.assert_called_once()
    mock_start.assert_called_once()


def test_cli_daemon_logs(tmp_path: Path) -> None:
    runner = CliRunner()
    log_file = tmp_path / "daemon.log"
    log_file.write_text("line1\nline2\nline3\nline4\nline5\n")

    with patch("minidispatch.core.daemon.DAEMON_LOG", str(log_file)):
        # Positive n shows from start
        res = runner.invoke(app, ["daemon", "logs", "-n", "2"])
        assert res.exit_code == 0
        assert "line1" in res.stdout
        assert "line2" in res.stdout
        assert "line3" not in res.stdout

        # Negative n shows from end
        res = runner.invoke(app, ["daemon", "logs", "-n", "-2"])
        assert res.exit_code == 0
        assert "line4" in res.stdout
        assert "line5" in res.stdout
        assert "line3" not in res.stdout
