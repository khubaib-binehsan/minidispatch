import os
import signal
import subprocess
import sys
import time

from minidispatch.core.constants import DAEMON_LOG, DAEMON_PID, ensure_dirs
from minidispatch.core import utils


def is_running() -> bool:
    return utils.is_running(DAEMON_PID)


def stop() -> str:
    attempts = 0

    while attempts < 3:
        if not DAEMON_PID.exists():
            return "Daemon is not running."

        try:
            pid = int(DAEMON_PID.read_text().strip())
            os.kill(pid, signal.SIGINT)

            DAEMON_PID.unlink(missing_ok=True)

        except (ValueError, ProcessLookupError):
            DAEMON_PID.unlink(missing_ok=True)

        if not DAEMON_PID.exists():
            return "Daemon stopped."

        attempts += 1

    return "Failed to stop daemon."


def start() -> None:
    if is_running():
        return

    ensure_dirs()

    # This is the watchdog process logic
    # We will fork twice to properly daemonize
    parent_pid = os.fork()
    if parent_pid > 0:
        return  # parent (cli) exit

    os.setsid()

    parent_pid = os.fork()
    if parent_pid > 0:
        sys.exit(0)  # Second parent exit

    # Now in the daemonized watchdog process
    # We write the PID of the watchdog process, not the subprocess
    DAEMON_PID.write_text(str(os.getpid()))

    process: subprocess.Popen | None = None

    def handle_exit(signum: int, frame: object) -> None:
        if process:
            process.terminate()
            process.wait()

        sys.exit(0)

    # exits the subprocess as well on SIGINT and SIGTERM
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

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
    time.sleep(0.5)

    if is_running():
        pid = DAEMON_PID.read_text().strip()

        return f"Daemon is running (PID: {pid})"

    return "Daemon is stopped."
