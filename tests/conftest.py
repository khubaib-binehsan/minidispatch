from __future__ import annotations

import hashlib
import os
import re
import shutil
from pathlib import Path

import pytest

from minidispatch.internal.test_env import activate_test_env

project_root = Path(__file__).resolve().parents[1]

_TEST_HOME = activate_test_env(project_root)


@pytest.fixture(scope="session")
def test_home() -> Path:
    return _TEST_HOME


@pytest.fixture(autouse=True)
def reset_db() -> None:
    from minidispatch.core.constants import DB_PATH
    from minidispatch.db import manager as db_manager

    if DB_PATH.exists():
        DB_PATH.unlink(missing_ok=True)

    db_manager._initialized = False


@pytest.fixture()
def workdir(test_home: Path, request: pytest.FixtureRequest) -> Path:
    node_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", request.node.nodeid)
    path = test_home / "work" / node_id

    if path.exists():
        shutil.rmtree(path, ignore_errors=True)

    path.mkdir(parents=True, exist_ok=True)
    return path


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    if os.environ.get("MINIDISPATCH_TEST_SEED_INSPECT", "1") == "0":
        return

    from minidispatch.db import manager as db_manager

    try:
        command = "echo inspect"
        cron = "0 0 * * *"
        job_id = hashlib.sha256(f"{command}{cron}".encode()).hexdigest()[:8]
        db_manager.add_job(
            job_id=job_id,
            name="inspect",
            pwd=str(_TEST_HOME),
            command=command,
            cron=cron,
            timeout=None,
        )
    except Exception:
        return
