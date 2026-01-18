from __future__ import annotations

import os
from pathlib import Path


def activate_test_env(project_root: Path) -> Path:
    """Activate an isolated test env for the current pytest process.

    This only affects the current Python process (pytest). It does not modify
    your shell or any environment outside the test run.

    Creates/uses a real directory under the repo so you can inspect artifacts.
    """

    test_home = project_root / ".minidispatch_test_env"

    test_home.mkdir(parents=True, exist_ok=True)

    os.environ["MINI_DISPATCH_HOME"] = str(test_home)
    os.environ["MINI_DISPATCH_DB"] = str(test_home / "database.sqlite")
    os.environ["MINI_DISPATCH_LOGS"] = str(test_home / "logs")
    os.environ["MINI_DISPATCH_DAEMON_LOG"] = str(test_home / "logs" / "daemon.log")
    os.environ["MINI_DISPATCH_DAEMON_PID"] = str(test_home / "daemon.pid")
    os.environ["MINI_DISPATCH_JOBS_LOGS"] = str(test_home / "jobs_logs")
    os.environ["MINI_DISPATCH_ENVS"] = str(test_home / "envs")

    return test_home
