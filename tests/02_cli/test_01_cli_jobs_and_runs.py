from __future__ import annotations

import hashlib
from pathlib import Path

from typer.testing import CliRunner

from minidispatch.db import manager as db_manager
from minidispatch.main import app


def _seed_one_job(workdir: Path) -> str:
    command = "echo hello"
    cron = "0 0 * * *"
    job_id = hashlib.sha256(f"{command}{cron}".encode()).hexdigest()[:8]

    db_manager.add_job(
        job_id=job_id,
        name="example",
        pwd=str(workdir),
        command=command,
        cron=cron,
        timeout=None,
    )

    return job_id


def _seed_run(job_id: str, status: str) -> None:
    with db_manager.get_connection() as conn:
        conn.execute(
            "INSERT INTO runs (id, job_id, start_time, end_time, status, pid) VALUES (?, ?, ?, ?, ?, ?)",
            (
                f"run_{status}",
                job_id,
                "2020-01-01T00:00:00",
                "2020-01-01T00:00:01",
                status,
                None,
            ),
        )
        conn.commit()


def test_cli_jobs_no_jobs() -> None:
    runner = CliRunner()

    res = runner.invoke(app, ["jobs"])

    assert res.exit_code == 0
    assert "No jobs found." in res.stdout


def test_cli_jobs_lists_seeded_job(workdir: Path) -> None:
    job_id = _seed_one_job(workdir)
    runner = CliRunner()

    res = runner.invoke(app, ["jobs", "-n", "1"])

    assert res.exit_code == 0
    assert job_id in res.stdout


def test_cli_jobs_list_shows_only_names(workdir: Path) -> None:
    _seed_one_job(workdir)
    runner = CliRunner()

    res = runner.invoke(app, ["jobs", "--list"])

    assert res.exit_code == 0
    assert "example" in res.stdout
    assert "Cron" not in res.stdout
    assert "Command" not in res.stdout


def test_cli_jobs_success_failure_filters(workdir: Path) -> None:
    job_id = _seed_one_job(workdir)
    _seed_run(job_id, "success")
    runner = CliRunner()

    res_success = runner.invoke(app, ["jobs", "--success"])
    assert res_success.exit_code == 0
    assert job_id in res_success.stdout

    res_failure = runner.invoke(app, ["jobs", "--failure"])
    assert res_failure.exit_code == 0
    assert job_id not in res_failure.stdout


def test_cli_job_not_found_exits_1() -> None:
    runner = CliRunner()

    res = runner.invoke(app, ["job", "missing"])

    assert res.exit_code == 1
    assert "job not found" in res.stdout.lower()


def test_cli_job_shows_extended_details(workdir: Path) -> None:
    job_id = _seed_one_job(workdir)
    _seed_run(job_id, "success")
    runner = CliRunner()

    res = runner.invoke(app, ["job", job_id])

    assert res.exit_code == 0
    out = res.stdout.lower()
    assert "last run" in out
    assert "last run success" in out
    assert "is currently running" in out
    assert "next run" in out


def test_cli_runs_scheduled_for_seeded_job(workdir: Path) -> None:
    job_id = _seed_one_job(workdir)
    runner = CliRunner()

    res = runner.invoke(app, ["runs", job_id, "--scheduled", "-n", "1"])

    assert res.exit_code == 0
    assert "scheduled" in res.stdout.lower()


def test_cli_job_no_args_shows_help() -> None:
    runner = CliRunner()
    res = runner.invoke(app, ["job"])
    assert res.exit_code == 0
    assert "Usage:" in res.stdout


def test_cli_runs_no_args_shows_help() -> None:
    runner = CliRunner()
    res = runner.invoke(app, ["runs"])
    assert res.exit_code == 0
    assert "Usage:" in res.stdout


def test_cli_runs_job_not_found_exits_1() -> None:
    runner = CliRunner()
    res = runner.invoke(app, ["runs", "missing"])
    assert res.exit_code == 1
    assert "job not found" in res.stdout.lower()


def test_cli_runs_pagination(workdir: Path) -> None:
    job_id = _seed_one_job(workdir)
    _seed_run(job_id, "success")
    _seed_run(job_id, "failed")

    runner = CliRunner()

    # Show 1
    res = runner.invoke(app, ["runs", job_id, "-n", "1"])
    assert res.exit_code == 0
    assert "run_success" in res.stdout or "run_failed" in res.stdout
    # Count rows in output is hard due to rich, but we can check presence

    # Show 0
    res = runner.invoke(app, ["runs", job_id, "-n", "0"])
    assert res.exit_code == 0
    assert "run_success" not in res.stdout
    assert "run_failed" not in res.stdout
