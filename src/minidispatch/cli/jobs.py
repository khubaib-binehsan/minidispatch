import typer
from typing import Optional


def create_jobs_app() -> typer.Typer:
    app = typer.Typer(help="List and view jobs.", no_args_is_help=True)

    @app.callback(invoke_without_command=True)
    def jobs(
        ctx: typer.Context,
        job: Optional[str] = typer.Argument(None, help="Job name or ID"),
        short: bool = typer.Option(
            False, "--short", help="List jobs with no additional details"
        ),
        failed: bool = typer.Option(False, "--failed", help="Show failed jobs/runs"),
        success: bool = typer.Option(
            False, "--success", help="Show successful jobs/runs"
        ),
        runs: bool = typer.Option(False, "-r", "--runs", help="Show individual runs"),
        num: int = typer.Option(10, "-n", help="Number of items to show"),
    ) -> None:
        "List jobs (and runs) with minimal details."

        if ctx.invoked_subcommand is None:
            typer.echo(
                f"Jobs status: job={job}, failed={failed}, success={success}, runs={runs}, n={num}"
            )

    return app
