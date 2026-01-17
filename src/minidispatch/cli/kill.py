from typing import Optional

import click
import typer


def kill(
    job_id: Optional[str] = typer.Option(None, "--job", help="Job name or ID"),
) -> None:
    "Kill a specific run of a job."

    if job_id is None:
        ctx = click.get_current_context()
        typer.echo(ctx.get_help())
        raise typer.Exit(0)

    typer.echo(f"Job details for: {job_id}")

    pass
