import os
from pathlib import Path

# Use current directory for development if MINIDISPATCH_HOME is not set
HOME = Path(os.environ.get("MINI_DISPATCH_HOME", Path.home() / ".minidispatch"))

DB_PATH = Path(os.environ.get("MINI_DISPATCH_DB", HOME / "database.sqlite"))
LOGS_DIR = Path(os.environ.get("MINI_DISPATCH_LOGS", HOME / "logs"))
DAEMON_LOG = Path(os.environ.get("MINI_DISPATCH_DAEMON_LOG", LOGS_DIR / "daemon.log"))
DAEMON_PID = Path(os.environ.get("MINI_DISPATCH_DAEMON_PID", LOGS_DIR / "DAEMON.pid"))
JOBS_LOGS_DIR = Path(os.environ.get("MINI_DISPATCH_JOBS_LOGS", LOGS_DIR / "jobs"))
ENVS_DIR = Path(os.environ.get("MINI_DISPATCH_ENVS", HOME / "envs"))


CONFIG_MAP = {
    "MINI_DISPATCH_HOME": HOME,
    "MINI_DISPATCH_DB": DB_PATH,
    "MINI_DISPATCH_LOGS": LOGS_DIR,
    "MINI_DISPATCH_DAEMON_LOG": DAEMON_LOG,
    "MINI_DISPATCH_DAEMON_PID": DAEMON_PID,
    "MINI_DISPATCH_JOBS_LOGS": JOBS_LOGS_DIR,
    "MINI_DISPATCH_ENVS": ENVS_DIR,
}


def ensure_dirs() -> None:
    HOME.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    JOBS_LOGS_DIR.mkdir(parents=True, exist_ok=True)
    ENVS_DIR.mkdir(parents=True, exist_ok=True)
