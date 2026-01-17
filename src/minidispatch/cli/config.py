import typer
from rich.console import Console
from rich.table import Table

from minidispatch.core.constants import CONFIG_MAP

console = Console()


def create_config_app() -> typer.Typer:
    app = typer.Typer(help="Manage configuration.", no_args_is_help=True)

    @app.command("list")
    def list_config() -> None:
        """List all configuration values and their current values."""
        table = Table(title="minidispatch Configuration")
        table.add_column("Environment Variable", style="cyan")
        table.add_column("Current Value", style="magenta")

        for env_var, value in CONFIG_MAP.items():
            table.add_row(env_var, str(value))

        console.print(table)

    @app.command("get")
    def get_config(
        key: str = typer.Argument(..., help="Config key (e.g., MINI_DISPATCH_DB)"),
    ) -> None:
        """Get the value of a specific configuration key."""
        if key in CONFIG_MAP:
            console.print(f"[cyan]{key}[/cyan] = [magenta]{CONFIG_MAP[key]}[/magenta]")
        else:
            console.print(f"[red]Key '{key}' not found.[/red]")
            raise typer.Exit(1)

    @app.command("set")
    def set_config() -> None:
        """Instruction on how to set configuration and show fallback template."""
        fallback_table = Table()
        fallback_table.add_column("Variable")
        fallback_table.add_column("Fallback Pattern")

        fallback_table.add_row("MINI_DISPATCH_HOME", "~/.minidispatch")
        fallback_table.add_row(
            "MINI_DISPATCH_DB", "$MINI_DISPATCH_HOME/database.sqlite"
        )
        fallback_table.add_row("MINI_DISPATCH_LOGS", "$MINI_DISPATCH_HOME/logs")
        fallback_table.add_row(
            "MINI_DISPATCH_DAEMON_LOG", "$MINI_DISPATCH_LOGS/daemon.log"
        )
        fallback_table.add_row(
            "MINI_DISPATCH_DAEMON_PID", "$MINI_DISPATCH_LOGS/DAEMON.pid"
        )
        fallback_table.add_row("MINI_DISPATCH_JOBS_LOGS", "$MINI_DISPATCH_LOGS/jobs")
        fallback_table.add_row("MINI_DISPATCH_ENVS", "$MINI_DISPATCH_HOME/envs")

        console.print(fallback_table)

    return app
