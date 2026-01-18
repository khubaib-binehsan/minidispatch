from __future__ import annotations

import os
from pathlib import Path

from minidispatch.core.utils import is_running


def test_is_running_returns_false_and_deletes_invalid_pid(workdir: Path) -> None:
    pid_file = workdir / "test.pid"
    pid_file.write_text("not-a-pid")

    assert is_running(pid_file) is False
    assert pid_file.exists() is False


def test_is_running_returns_true_for_current_pid(workdir: Path) -> None:
    pid_file = workdir / "test.pid"
    pid_file.write_text(str(os.getpid()))

    assert is_running(pid_file) is True
    assert pid_file.exists() is True
