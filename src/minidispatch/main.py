# only intended to be run as a script

import typer

from minidispatch.cli.daemon import create_daemon_app

app = typer.Typer(no_args_is_help=True)


@app.callback()
def callback() -> None:
    "minidispatch: cronjob on steroids"
    pass


app.add_typer(create_daemon_app(), name="daemon")


if __name__ == "__main__":
    app()
