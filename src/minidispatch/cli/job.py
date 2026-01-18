import os
from typing import Optional

import click
import typer
from rich.console import Console
from rich.table import Table

from minidispatch.db import manager as db_manager


def _is_success(status: Optional[str]) -> Optional[bool]:
    if status is None:
        return None

    normalized = status.strip().lower()

    if normalized in {"success", "succeeded", "ok"}:
        return True
    if normalized in {"failed", "failure", "error"}:
        return False

    return None


def _pid_is_running(pid: Optional[int]) -> bool:
    if pid is None:
        return False

    try:
        os.kill(pid, 0)
        return True

    except ProcessLookupError:
        return False

    except PermissionError:
        return True


console = Console()


def job(
    job_id: Optional[str] = typer.Argument(None, help="Job name or ID"),
) -> None:
    "Show details for a specific job."

    if job_id is None:
        ctx = click.get_current_context()
        typer.echo(ctx.get_help())
        raise typer.Exit(0)

    job_data = db_manager.get_job(job_id)

    if not job_data:
        console.print(f"[red]Job not found: {job_id}[/red]")
        raise typer.Exit(1)

    table = Table(title=f"Job Details: {job_data['name']}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("ID", job_data["id"])
    table.add_row("Name", job_data["name"])
    table.add_row("Cron", job_data["cron"])
    table.add_row("Command", job_data["command"])
    table.add_row("PWD", job_data["pwd"])
    table.add_row("Timeout", str(job_data["timeout"]))

    resolved_job_id = job_data["id"]

    last_run_row = db_manager.get_job_last_run(resolved_job_id)
    last_run = ""
    last_run_success: Optional[bool] = None

    if last_run_row is not None:
        last_run = (last_run_row["end_time"] or last_run_row["start_time"]) or ""
        last_run_success = _is_success(last_run_row["status"])

    is_currently_running = _pid_is_running(job_data["pid"])

    next_run_row = db_manager.get_job_next_scheduled_run(resolved_job_id)
    next_run = "" if next_run_row is None else (next_run_row["scheduled_time"] or "")

    table.add_row("Last Run", last_run)
    table.add_row(
        "Last Run Success", "" if last_run_success is None else str(last_run_success)
    )
    table.add_row("Is Currently Running", str(is_currently_running))
    table.add_row("Next Run", next_run)

    console.print(table)
