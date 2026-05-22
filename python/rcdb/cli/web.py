import os
import click

from rcdb import web as rcdb_web, RCDBProvider
from .context import pass_rcdb_context


@click.command("web")
@click.option('--add-db', multiple=True,
              help='Add a named database as NAME=CONNECTION_STRING. Can be specified multiple times.')
@pass_rcdb_context
def web_command(context, add_db):
    """
    Runs the local RCDB web application using the connection string from
    either the CLI context or the RCDB_CONNECTION environment variable.

    Use --add-db to enable a database selector in the web UI:

        rcdb -c mysql://rcdb@host/rcdb web \\
            --add-db "Production=mysql://rcdb@prodhost/rcdb" \\
            --add-db "Test=mysql://rcdb@testhost/rcdb_test"
    """

    # Resolve the default connection string
    rcdb_provider = context.db
    if rcdb_provider and rcdb_provider.connection_string:
        assert isinstance(rcdb_provider, RCDBProvider)
        connection_string = rcdb_provider.connection_string
    elif "RCDB_CONNECTION" in os.environ:
        connection_string = os.environ["RCDB_CONNECTION"]
    else:
        connection_string = None

    # Parse --add-db entries into AVAILABLE_DATABASES
    if add_db:
        available = {}
        for entry in add_db:
            if '=' not in entry:
                click.echo(f"ERROR: --add-db value must be NAME=CONNECTION_STRING, got: {entry}")
                raise SystemExit(1)
            name, conn = entry.split('=', 1)
            name = name.strip()
            conn = conn.strip()
            if not name or not conn:
                click.echo(f"ERROR: --add-db value must have non-empty NAME and CONNECTION_STRING: {entry}")
                raise SystemExit(1)
            available[name] = conn

        rcdb_web.app.config["AVAILABLE_DATABASES"] = available

        if connection_string:
            rcdb_web.app.config["DEFAULT_DATABASE"] = connection_string
        else:
            # No -c provided, use the first --add-db entry as default
            first_conn = next(iter(available.values()))
            rcdb_web.app.config["DEFAULT_DATABASE"] = first_conn
            connection_string = first_conn

        # SQL_CONNECTION_STRING is still needed as a fallback
        rcdb_web.app.config["SQL_CONNECTION_STRING"] = connection_string
    elif connection_string:
        rcdb_web.app.config["SQL_CONNECTION_STRING"] = connection_string
    else:
        click.echo("ERROR: no connection string found. Provide via CLI or RCDB_CONNECTION env variable.")
        raise SystemExit(1)

    # Start the Flask dev server
    rcdb_web.app.run()
