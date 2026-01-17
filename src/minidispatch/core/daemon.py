import os
import signal
import subprocess
import sys
import time

from minidispatch.core.constants import DAEMON_LOG, DAEMON_PID, ensure_dirs
from minidispatch.core import utils


def is_running() -> bool:
    return utils.is_running(DAEMON_PID)


def stop() -> None:
    if not DAEMON_PID.exists():
        return

    try:
        pid = int(DAEMON_PID.read_text().strip())
        os.kill(pid, signal.SIGTERM)

        DAEMON_PID.unlink(missing_ok=True)

    except (ValueError, ProcessLookupError):
        DAEMON_PID.unlink(missing_ok=True)


def start() -> None:
    if is_running():
        return

    ensure_dirs()

    # This is the watchdog process logic
    # We will fork twice to properly daemonize
    if os.fork() > 0:
        return  # Parent exit

    os.setsid()

    if os.fork() > 0:
        sys.exit(0)  # Second parent exit

    # Now in the daemonized watchdog process
    DAEMON_PID.write_text(str(os.getpid()))

    with open(DAEMON_LOG, "a") as log_file:
        while True:
            log_file.write(f"[{time.ctime()}] Starting daemon subprocess...\n")
            log_file.flush()

            try:
                # spawn the actual daemon subprocess
                process = subprocess.Popen(
                    [sys.executable, "-m", "minidispatch.internal.daemon"],
                    stdout=log_file,
                    stderr=log_file,
                    start_new_session=True,
                )

                process.wait()
                log_file.write(
                    f"[{time.ctime()}] Daemon subprocess exited with code {process.returncode}.\n"
                )

            except Exception as e:
                log_file.write(f"[{time.ctime()}] Error spawning daemon: {e}\n")

            log_file.flush()
            time.sleep(5)


def get_status() -> str:
    if is_running():
        pid = DAEMON_PID.read_text().strip()

        return f"Daemon is running (PID: {pid})"

    return "Daemon is stopped."
