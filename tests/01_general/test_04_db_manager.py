from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

from minidispatch.core.constants import DB_PATH
from minidispatch.db import manager


def _tables(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()

    return {row[0] for row in rows}


def test_init_db_creates_tables() -> None:
    manager.init_db()

    assert DB_PATH.exists()

    with manager.get_connection() as conn:
        tables = _tables(conn)

    assert {"jobs", "runs", "scheduled_runs"}.issubset(tables)


def test_add_job_schedules_runs(workdir: Path) -> None:
    command = "echo hello"
    cron = "0 0 * * *"
    job_id = hashlib.sha256(f"{command}{cron}".encode()).hexdigest()[:8]
    manager.add_job(
        job_id=job_id,
        name="example",
        pwd=str(workdir),
        command=command,
        cron=cron,
        timeout=None,
    )

    job = manager.get_job(job_id)
    assert job is not None
    assert job["name"] == "example"

    scheduled = manager.get_job_scheduled_runs(job_id)
    assert 1 <= len(scheduled) <= 31


def test_get_job_next_scheduled_run_returns_next_future(workdir: Path) -> None:
    command = "echo hello"
    cron = "0 0 * * *"
    job_id = hashlib.sha256(f"{command}{cron}".encode()).hexdigest()[:8]
    manager.add_job(
        job_id=job_id,
        name="example",
        pwd=str(workdir),
        command=command,
        cron=cron,
        timeout=None,
    )

    next_row = manager.get_job_next_scheduled_run(job_id)

    assert next_row is not None
    assert next_row["job_id"] == job_id
    assert isinstance(next_row["scheduled_time"], str)


def test_get_job_last_run_returns_latest_by_end_time(workdir: Path) -> None:
    command = "echo hello"
    cron = "0 0 * * *"
    job_id = hashlib.sha256(f"{command}{cron}".encode()).hexdigest()[:8]
    manager.add_job(
        job_id=job_id,
        name="example",
        pwd=str(workdir),
        command=command,
        cron=cron,
        timeout=None,
    )

    manager.init_db()

    with manager.get_connection() as conn:
        conn.execute(
            "INSERT INTO runs (id, job_id, start_time, end_time, status, pid) VALUES (?, ?, ?, ?, ?, ?)",
            (
                "run_old",
                job_id,
                "2020-01-01T00:00:00",
                "2020-01-01T00:00:01",
                "failure",
                None,
            ),
        )
        conn.execute(
            "INSERT INTO runs (id, job_id, start_time, end_time, status, pid) VALUES (?, ?, ?, ?, ?, ?)",
            (
                "run_new",
                job_id,
                "2020-01-02T00:00:00",
                "2020-01-02T00:00:01",
                "success",
                None,
            ),
        )
        conn.commit()

    last = manager.get_job_last_run(job_id)
    assert last is not None
    assert last["id"] == "run_new"
    assert last["status"] == "success"


def test_remove_job_deletes_job_and_schedules(workdir: Path) -> None:
    command = "echo hello"
    cron = "0 0 * * *"
    job_id = hashlib.sha256(f"{command}{cron}".encode()).hexdigest()[:8]
    manager.add_job(
        job_id=job_id,
        name="example",
        pwd=str(workdir),
        command=command,
        cron=cron,
        timeout=None,
    )

    assert manager.get_job(job_id) is not None
    assert len(manager.get_job_scheduled_runs(job_id)) > 0

    manager.remove_job(job_id)

    assert manager.get_job(job_id) is None
    assert manager.get_job_scheduled_runs(job_id) == []
