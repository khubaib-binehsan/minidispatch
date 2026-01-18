import click
import sqlite3
from typing import Optional

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


console = Console()


def jobs(
    jobs_list: Optional[bool] = typer.Option(
        None,
        "--list",
        help="List jobs (deprecated: listing is the default now)",
    ),
    success: bool = typer.Option(
        False,
        "--success",
        help="Show jobs whose last run succeeded",
    ),
    failure: bool = typer.Option(
        False,
        "--failure",
        help="Show jobs whose last run failed",
    ),
    num: int = typer.Option(
        10,
        "-n",
        help="Number of items to show (10 = first 10, -10 = last 10)",
    ),
) -> None:
    "List jobs with minimal details."

    if jobs_list is False:
        ctx = click.get_current_context()
        typer.echo(ctx.get_help())
        raise typer.Exit(0)

    jobs_data = db_manager.get_jobs()

    if not jobs_data:
        typer.echo("No jobs found.")
        return

    jobs_with_last: list[tuple[sqlite3.Row, Optional[bool]]] = []
    for job_row in jobs_data:
        last_run_row = db_manager.get_job_last_run(job_row["id"])
        last_run_success = _is_success(
            None if last_run_row is None else last_run_row["status"]
        )
        jobs_with_last.append((job_row, last_run_success))

    if success and not failure:
        jobs_with_last = [j for j in jobs_with_last if j[1] is True]
    elif failure and not success:
        jobs_with_last = [j for j in jobs_with_last if j[1] is False]

    if jobs_list is True:
        for job_row, _last in jobs_with_last:
            typer.echo(job_row["name"] or job_row["id"])
        return

    jobs_data = [j[0] for j in jobs_with_last]

    if num == 0:
        jobs_data = []
    elif num < 0:
        jobs_data = jobs_data[-abs(num) :]
    else:
        jobs_data = jobs_data[:num]

    table = Table(title="Jobs")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("last_run_success", style="white")
    table.add_column("Cron", style="green")
    table.add_column("Command", style="yellow")

    for job_row in jobs_data:
        last_run_row = db_manager.get_job_last_run(job_row["id"])
        last_run_success = _is_success(
            None if last_run_row is None else last_run_row["status"]
        )
        last_run_success_str = "" if last_run_success is None else str(last_run_success)
        table.add_row(
            job_row["id"],
            job_row["name"],
            last_run_success_str,
            job_row["cron"],
            job_row["command"],
        )

    console.print(table)
