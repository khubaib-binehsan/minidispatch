import typer

from minidispatch.core import daemon


def create_daemon_app() -> typer.Typer:
    app = typer.Typer(help="Manage the daemon process.", no_args_is_help=True)

    @app.command()
    def start(
        restart: bool = typer.Option(False, "-f", "--force", help="Restart the daemon"),
    ) -> None:
        "Start/Restart the daemon process."

        if daemon.is_running() and not restart:
            typer.echo(daemon.get_status())

        else:
            if daemon.is_running() and restart:
                typer.echo("Restarting daemon...")
                daemon.stop()
            else:
                typer.echo("Starting daemon...")

            daemon.start()
            typer.echo(daemon.get_status())

    @app.command()
    def stop() -> None:
        "Stop the daemon process."
        if daemon.is_running():
            typer.echo("Stopping daemon...")
            daemon.stop()
        else:
            typer.echo("Daemon is not running.")

    @app.command()
    def status() -> None:
        "Get the daemon status."
        typer.echo(daemon.get_status())

    @app.command()
    def restart() -> None:
        "Restart the daemon process."
        typer.echo("Restarting daemon...")
        daemon.stop()
        daemon.start()
        typer.echo(daemon.get_status())

    return app
