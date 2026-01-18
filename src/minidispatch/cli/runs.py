from __future__ import annotations

from datetime import datetime
from typing import Optional

import click
import typer
from rich.console import Console
from rich.table import Table

from minidispatch.db import manager as db_manager

console = Console()


def _parse_iso_dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def runs(
    job_id: Optional[str] = typer.Argument(None, help="Job name or ID"),
    scheduled: bool = typer.Option(
        False, "--scheduled", help="Show scheduled runs only"
    ),
    num: int = typer.Option(
        10,
        "-n",
        help="Number of items to show (10 = first 10, -10 = last 10)",
    ),
) -> None:
    "Show all runs for a job (scheduled + executed)."

    if job_id is None:
        ctx = click.get_current_context()
        typer.echo(ctx.get_help())
        raise typer.Exit(0)

    job_row = db_manager.get_job(job_id)
    if not job_row:
        console.print(f"[red]Job not found: {job_id}[/red]")
        raise typer.Exit(1)

    resolved_job_id = job_row["id"]

    scheduled_rows = db_manager.get_job_scheduled_runs(resolved_job_id)
    run_rows = [] if scheduled else db_manager.get_job_runs(resolved_job_id)

    entries: list[dict[str, str]] = []

    for row in scheduled_rows:
        entries.append(
            {
                "when": row["scheduled_time"],
                "type": "scheduled",
                "id": row["id"],
                "status": "scheduled",
                "pid": "",
                "start": "",
                "end": "",
            }
        )

    if not scheduled:
        for row in run_rows:
            start_time = row["start_time"] or ""
            end_time = row["end_time"] or ""
            pid = "" if row["pid"] is None else str(row["pid"])
            status = row["status"] or ""
            entries.append(
                {
                    "when": start_time,
                    "type": "run",
                    "id": row["id"],
                    "status": status,
                    "pid": pid,
                    "start": start_time,
                    "end": end_time,
                }
            )

    entries.sort(key=lambda e: _parse_iso_dt(e["when"]) if e["when"] else datetime.min)

    if num == 0:
        entries = []
    elif num < 0:
        entries = entries[-abs(num) :]
    else:
        entries = entries[:num]

    table = Table(title=f"Runs: {job_row['name']} ({resolved_job_id})")
    table.add_column("When", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("ID", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("PID", style="white")
    table.add_column("Start", style="cyan")
    table.add_column("End", style="cyan")

    for e in entries:
        table.add_row(
            e["when"],
            e["type"],
            e["id"],
            e["status"],
            e["pid"],
            e["start"],
            e["end"],
        )

    console.print(table)
