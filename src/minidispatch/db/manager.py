import sqlite3
from typing import Optional

from minidispatch.core.constants import DB_PATH
from minidispatch.db import sql


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(sql.JOBS)
        conn.execute(sql.RUNS)
        conn.execute(sql.SCHEDULED_RUNS)
        conn.commit()


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
