import hashlib
import os
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from minidispatch.core import daemon as daemon_core
from minidispatch.core.constants import ENVS_DIR
from minidispatch.db import jobnames
from minidispatch.db import manager as db_manager

console = Console()


def submit(
    cron: str = typer.Argument(..., help="Cron schedule"),
    command: str = typer.Argument(..., help="Command to run"),
    name: Optional[str] = typer.Option(None, "--name", help="Job name"),
    timeout: Optional[int] = typer.Option(
        600, "--timeout", help="Job timeout in seconds"
    ),
) -> None:
    "Submit a new job."

    # Capture environment details
    pwd = os.getcwd()
    env_vars = dict(os.environ)

    # Generate a unique job ID (hash of command and cron)
    job_hash = hashlib.sha256(f"{command}{cron}".encode()).hexdigest()[:8]
    job_id = job_hash

    if not name:
        name = jobnames.generate_name()

    # Start daemon if not running
    if not daemon_core.is_running():
        console.print("[yellow]Daemon not running, starting daemon...[/yellow]")
        daemon_core.start()

    # Save environment variables to a file
    ENVS_DIR.mkdir(parents=True, exist_ok=True)
    env_file = ENVS_DIR / f"{job_id}.env"
    try:
        with open(env_file, "w") as f:
            for k, v in env_vars.items():
                # Basic escaping for shell
                f.write(f'export {k}="{v}"\n')
    except Exception as e:
        console.print(f"[red]Error saving environment file: {e}[/red]")
        raise typer.Exit(1)

    # Save to database
    try:
        db_manager.add_job(job_id, name, pwd, command, cron, timeout)

        table = Table(title="Job Submitted Successfully")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("ID", job_id)
        table.add_row("Name", name)
        table.add_row("Cron", cron)
        table.add_row("Command", command)

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error submitting job: {e}[/red]")
        raise typer.Exit(1)
