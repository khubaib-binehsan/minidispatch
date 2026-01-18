from minidispatch.db import sql


def test_sql_executes_in_sqlite() -> None:
    import sqlite3

    conn = sqlite3.connect(":memory:")
    try:
        conn.execute(sql.JOBS)
        conn.execute(sql.RUNS)
        conn.execute(sql.SCHEDULED_RUNS)

        for statement in sql.INDICES:
            conn.execute(statement)

    finally:
        conn.close()


def test_sql_has_expected_tables() -> None:
    assert "CREATE TABLE IF NOT EXISTS jobs" in sql.JOBS
    assert "CREATE TABLE IF NOT EXISTS runs" in sql.RUNS
    assert "CREATE TABLE IF NOT EXISTS scheduled_runs" in sql.SCHEDULED_RUNS


def test_sql_indices_are_present() -> None:
    assert len(sql.INDICES) >= 1
    assert all("CREATE INDEX IF NOT EXISTS" in stmt for stmt in sql.INDICES)
