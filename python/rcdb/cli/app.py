import os
import click

from rcdb.app_context import RcdbApplicationContext
from rcdb.version import version as rcdb_version

from .ls import ls_command
from .repair import repair_command
from .db import db_command
from .rp import rp_command
from .web import web_command
from .info import info_command
from .add import add_command
from .select import select_command
from .file import file_command
from .run import run_command


pass_rcdb_context = click.make_pass_decorator(RcdbApplicationContext)


def get_default_config_path():
    return os.path.join(os.path.expanduser('~'), '.rcdb_user')


class RcdbGroup(click.Group):
    """Top level group that treats `rcdb <number>` as `rcdb run <number>`."""

    def resolve_command(self, ctx, args):
        # If the first token is not a known command but looks like a run number,
        # dispatch to the `run` command, i.e. `rcdb 1000` == `rcdb run 1000`.
        if args and args[0] not in self.commands and args[0].isdigit():
            args = ["run"] + args
        return super().resolve_command(ctx, args)


@click.group(cls=RcdbGroup, invoke_without_command=True)
@click.option('--user-config', envvar='RCDB_USER_CONFIG', default=get_default_config_path, metavar='PATH', help='Changes the user config location.')
@click.option('--connection', '-c', envvar='RCDB_CONNECTION', help='Database connection string', default=None, required=False)
@click.option('--config', nargs=2, multiple=True, metavar='KEY VALUE', help='Overrides a config key/value pair.')
@click.option('--verbose', '-v', is_flag=True, help='Enables verbose mode.')
@click.version_option(rcdb_version)
@click.pass_context
def rcdb_cli(ctx, user_config, connection, config, verbose):
    """'rcdb' is a RCDB (run conditions database) command line tool
    This tool allows to select runs and get values as well as manage RCDB values

    RCDB CLI needs a DB connection string which could be provided via:
    - RCDB_CONNECTION environment variable
    - -c/--connection flag
    """

    # Create a rcdb_app_context object and remember it as the context object.  From
    # this point onwards other commands can refer to it by using the
    # @pass_rcdb_context decorator. A connection is not validated here so that
    # `--help` and connection-less commands stay clean; commands that need a
    # database call context.require_connected_db() to get a clear error instead.
    ctx.obj = RcdbApplicationContext(os.path.abspath(user_config), connection)
    ctx.obj.verbose = verbose
    for key, value in config:
        ctx.obj.set_config(key, value)

    # Dispose the DB engine deterministically when the command finishes, rather
    # than leaving it to garbage collection. On Python 3.13+ a lingering, GC'd
    # SQLite connection emits "ResourceWarning: unclosed database" at an
    # unpredictable time, which can leak into command output captured by tests.
    ctx.call_on_close(ctx.obj.close)

    # Bo commands given
    if ctx.invoked_subcommand is None:
        # There is a connection but no subcommand
        if connection:
            # If user typed just `rcdb -c <db>`, call info() automatically:
            ctx.invoke(info_command)        # => invoke the "info" command
        else:
            # No subcommand, no connection => show help
            click.echo(ctx.get_help())


# Add commands to application
rcdb_cli.add_command(ls_command)
rcdb_cli.add_command(repair_command)
rcdb_cli.add_command(db_command)
rcdb_cli.add_command(rp_command)
rcdb_cli.add_command(web_command)
rcdb_cli.add_command(info_command)
rcdb_cli.add_command(add_command)
rcdb_cli.add_command(select_command)
rcdb_cli.add_command(file_command)
rcdb_cli.add_command(run_command)

