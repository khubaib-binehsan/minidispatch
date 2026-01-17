from typing import Optional

import click
import typer


def job(
    job_id: Optional[str] = typer.Argument(None, help="Job name or ID"),
) -> None:
    "Show details for a specific job."

    if job_id is None:
        ctx = click.get_current_context()
        typer.echo(ctx.get_help())
        raise typer.Exit(0)

    typer.echo(f"Job details for: {job_id}")
