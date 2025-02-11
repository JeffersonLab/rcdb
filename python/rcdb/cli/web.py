import os
import click

from rcdb import web as rcdb_web
from .context import pass_rcdb_context


@click.command("web")
@pass_rcdb_context
def web(context):
    """
    Runs the local RCDB web application using the connection string from
    either the CLI context or the RCDB_CONNECTION environment variable.
    """
    # If user provided --connection on the CLI, context.db.connection_str is set:
    if context.db and context.db.connect_str:
        rcdb_web.app.config["SQL_CONNECTION_STRING"] = context.db.connect_str
    elif "RCDB_CONNECTION" in os.environ:
        # Otherwise check the environment variable
        rcdb_web.app.config["SQL_CONNECTION_STRING"] = os.environ["RCDB_CONNECTION"]
    else:
        # If neither is present, show an error and exit
        click.echo("ERROR: no connection string found. Provide via CLI or RCDB_CONNECTION env variable.")
        raise SystemExit(1)

    # Start the Flask dev server
    rcdb_web.app.run()
