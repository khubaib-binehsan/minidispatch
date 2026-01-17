import click
import typer
from typing import Optional


def jobs(
    job: Optional[str] = typer.Option(None, "--job", help="Job name or ID"),
    short: bool = typer.Option(
        False, "--short", help="List jobs with no additional details"
    ),
    failed: bool = typer.Option(False, "--failed", help="Show failed jobs/runs"),
    success: bool = typer.Option(False, "--success", help="Show successful jobs/runs"),
    runs: bool = typer.Option(False, "-r", "--runs", help="Show individual runs"),
    num: int = typer.Option(10, "-n", help="Number of items to show"),
) -> None:
    "List jobs (and runs) with minimal details."

    ctx = click.get_current_context()
    typer.echo(ctx.get_help())
    raise typer.Exit(0)
