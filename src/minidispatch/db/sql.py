# sqlite tables

JOBS = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    name TEXT,
    pwd TEXT,
    command TEXT,
    cron TEXT,
    timeout INTEGER,
    pid INTEGER
);
"""

RUNS = """
CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY,
    job_id TEXT,
    start_time TEXT,
    end_time TEXT,
    status TEXT,
    pid INTEGER
);    
"""

SCHEDULED_RUNS = """
CREATE TABLE IF NOT EXISTS scheduled_runs (
    id TEXT PRIMARY KEY,
    job_id TEXT,
    scheduled_time TEXT
);
"""
