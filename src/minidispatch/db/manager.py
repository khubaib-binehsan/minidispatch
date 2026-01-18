import hashlib
import sqlite3
from datetime import datetime, timedelta
from typing import Optional

from croniter import croniter

from minidispatch.core.constants import DB_PATH, ensure_dirs
from minidispatch.db import sql

_initialized = False


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    global _initialized

    if _initialized:
        return

    ensure_dirs()

    with get_connection() as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute(sql.JOBS)
        conn.execute(sql.RUNS)
        conn.execute(sql.SCHEDULED_RUNS)

        for index_sql in sql.INDICES:
            conn.execute(index_sql)

        conn.commit()

    _initialized = True


def add_job(
    job_id: str,
    name: str,
    pwd: str,
    command: str,
    cron: str,
    timeout: Optional[int],
) -> None:
    init_db()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO jobs (id, name, pwd, command, cron, timeout) VALUES (?, ?, ?, ?, ?, ?)",
            (job_id, name, pwd, command, cron, timeout),
        )
        conn.commit()
    schedule_job_runs(job_id, cron)


def schedule_job_runs(job_id: str, cron_str: str) -> None:
    init_db()
    now = datetime.now()
    end_date = now + timedelta(days=30)

    iters = croniter(cron_str, now)

    scheduled_runs = []

    while True:
        next_run = iters.get_next(datetime)
        if next_run > end_date:
            break
        run_id = hashlib.sha256(f"{job_id}{next_run.isoformat()}".encode()).hexdigest()[
            :8
        ]
        scheduled_runs.append((run_id, job_id, next_run.isoformat()))

    with get_connection() as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO scheduled_runs (id, job_id, scheduled_time) VALUES (?, ?, ?)",
            scheduled_runs,
        )
        conn.commit()


def remove_job(job_id: str) -> None:
    init_db()

    with get_connection() as conn:
        conn.execute("DELETE FROM scheduled_runs WHERE job_id = ?", (job_id,))
        conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        conn.commit()


def remove_job_schedules(job_id: str) -> None:
    init_db()

    with get_connection() as conn:
        conn.execute("DELETE FROM scheduled_runs WHERE job_id = ?", (job_id,))
        conn.commit()


def get_jobs() -> list[sqlite3.Row]:
    init_db()

    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM jobs ORDER BY COALESCE(name, ''), id"
        ).fetchall()


def get_job(job_id: str) -> Optional[sqlite3.Row]:
    init_db()
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM jobs WHERE id = ? OR name = ?", (job_id, job_id)
        ).fetchone()


def get_job_runs(job_id: str) -> list[sqlite3.Row]:
    init_db()
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM runs WHERE job_id = ? ORDER BY start_time ASC", (job_id,)
        ).fetchall()


def get_job_scheduled_runs(job_id: str) -> list[sqlite3.Row]:
    init_db()
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM scheduled_runs WHERE job_id = ? ORDER BY scheduled_time ASC",
            (job_id,),
        ).fetchall()


def get_job_last_run(job_id: str) -> Optional[sqlite3.Row]:
    init_db()
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM runs WHERE job_id = ? ORDER BY COALESCE(end_time, start_time) DESC LIMIT 1",
            (job_id,),
        ).fetchone()


def get_job_next_scheduled_run(job_id: str) -> Optional[sqlite3.Row]:
    init_db()
    now = datetime.now().isoformat()
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM scheduled_runs WHERE job_id = ? AND scheduled_time >= ? ORDER BY scheduled_time ASC LIMIT 1",
            (job_id, now),
        ).fetchone()
