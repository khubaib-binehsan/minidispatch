import os
from pathlib import Path


def is_running(pid_file: Path) -> bool:
    if not pid_file.exists():
        return False

    try:
        pid = int(pid_file.read_text().strip())
        os.kill(pid, 0)

        return True

    except (ValueError, ProcessLookupError):
        pid_file.unlink(missing_ok=True)
        return False
