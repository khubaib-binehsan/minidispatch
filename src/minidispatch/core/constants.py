import os
from pathlib import Path

# Use current directory for development if MINIDISPATCH_HOME is not set
HOME = Path(
    os.environ.get(
        "MINI_DISPATCH_HOME",
        Path.home() / ".minidispatch",
    )
)

DB_PATH = HOME / "database.sqlite"
LOGS_DIR = HOME / "logs"
DAEMON_LOG = LOGS_DIR / "daemon.log"
DAEMON_PID = LOGS_DIR / "DAEMON.pid"
JOBS_LOGS_DIR = LOGS_DIR / "jobs"
ENVS_DIR = HOME / "envs"


def ensure_dirs() -> None:
    HOME.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    JOBS_LOGS_DIR.mkdir(parents=True, exist_ok=True)
    ENVS_DIR.mkdir(parents=True, exist_ok=True)
