# sqlite tables

JOBS = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE,
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

INDICES = [
    "CREATE INDEX IF NOT EXISTS idx_jobs_name ON jobs(name)",
    "CREATE INDEX IF NOT EXISTS idx_runs_job_id ON runs(job_id)",
    "CREATE INDEX IF NOT EXISTS idx_scheduled_runs_job_id ON scheduled_runs(job_id)",
    "CREATE INDEX IF NOT EXISTS idx_scheduled_runs_time ON scheduled_runs(scheduled_time)",
]
