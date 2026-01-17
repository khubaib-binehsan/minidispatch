# only intended to be run as a script

import typer

from minidispatch.cli.daemon import create_daemon_app
from minidispatch.cli.job import job
from minidispatch.cli.kill import kill
from minidispatch.cli.jobs import jobs
from minidispatch.cli.submit import submit

app = typer.Typer(no_args_is_help=True)


@app.callback()
def callback() -> None:
    "minidispatch: cronjob on steroids"
    pass


app.add_typer(create_daemon_app(), name="daemon")
app.command(name="jobs")(jobs)
app.command(name="job")(job)
app.command(name="kill")(kill)
app.command(name="submit")(submit)


if __name__ == "__main__":
    app()
