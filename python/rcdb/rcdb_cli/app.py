import os
import sys
import posixpath
import click
from click import Command

from rcdb.app_context import RcdbApplicationContext, parse_run_range
from rcdb import RCDBProvider
from rcdb.model import ConfigurationFile

from .ls import ls as ls_cmd
from .repair import repair as repair_grp
from .db import db as db_grp


pass_rcdb_context = click.make_pass_decorator(RcdbApplicationContext)


def get_default_config_path():
    return os.path.join(os.path.expanduser('~'), '.rcdb_user')


@click.group(invoke_without_command=True)
@click.option('--user-config', envvar='RCDB_USER_CONFIG', default=get_default_config_path,
              metavar='PATH', help='Changes the user config location.')
@click.option('--connection', '-c', envvar='RCDB_CONNECTION', help='Database connection string',
              default=None, required=False)
@click.option('--config', nargs=2, multiple=True,
              metavar='KEY VALUE', help='Overrides a config key/value pair.')
@click.option('--verbose', '-v', is_flag=True, help='Enables verbose mode.')
@click.version_option('1.0')
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
    # @pass_rcdb_context decorator.
    if not connection:
        print("(!)WARNING no connection provided! "
              "Provide DB connection string via --connection/-c or RCDB_CONNECTION environment variable.")
    ctx.obj = RcdbApplicationContext(os.path.abspath(user_config), connection)
    ctx.obj.verbose = verbose
    for key, value in config:
        ctx.obj.set_config(key, value)

    if ctx.invoked_subcommand is None:
        "No command was specified"
        click.echo(ctx.get_help())


# Add ls command
# noinspection PyTypeChecker
rcdb_cli.add_command(ls_cmd)

# Add 'repair' group of commands
# noinspection PyTypeChecker
rcdb_cli.add_command(repair_grp)

# Add 'db' group of commands
# noinspection PyTypeChecker
rcdb_cli.add_command(db_grp)



@rcdb_cli.command()
@pass_rcdb_context
@click.argument('run', required=True)
@click.option('--long', '-l', 'is_long', is_flag=True, help='Prints condition full information')
def files(context, run, is_long):
    """
    Shows files stored for a current run:

    RUN: Run number to show files for
    """
    db = context.db
    assert isinstance(db, RCDBProvider)

    run = db.get_run(int(run))

    for file in run.files:
        assert isinstance(file, ConfigurationFile)
        click.echo(file.path)


def cat():
    pass

def dump():
    pass


def _process_sel_args(args, ):
    """

    :param args: list of user arguments
    :param run_periods: db.get_run_periods() assumed
    :return: ((run_min, run_max), query, view)
    """

    run_range_str = ''
    for arg in args:
        if '-' in arg:
            run_range_str = arg
            args = [a for a in args if a!=arg]
            break

    if len(args) == 0:
        return run_range_str, None, None

    if len(args) == 1:
        return run_range_str, args[0], None

    return run_range_str, args[0], args[1]



@rcdb_cli.command()
@click.argument('query', required=None)
@click.argument('views_or_runs',  nargs=-1)
@click.option('--dump', '-d', 'is_dump_view', is_flag=True,
              help='Display results as to export to file. No borders, "#" comments')
@click.option('--desc/--asc', '-d/-a', 'is_descending', default=False,
              help="Sort order of run number descending or ascending")
@pass_rcdb_context
def sel(rcdb_context, query, views_or_runs, is_dump_view, is_descending):
    """ Command allows to select runs and get values from it"""
    assert isinstance(rcdb_context.db, RCDBProvider)
    args = [str(query)]
    args.extend([str(v) for v in views_or_runs])
    run_range_str, query, view = _process_sel_args(args)

    (run_min, run_max) = parse_run_range(run_range_str, rcdb_context.db.get_run_periods())

    if run_min is None:
        run_min = 0

    if run_max is None:
        run_max = sys.maxint

    if query == '@' or query is None:
        query = ''

    if not view:
        view = "event_count run_config"

    conditions_to_show = view.split()

    values = rcdb_context.db.select_values([], query, run_min, run_max)

    if not is_dump_view:
        try:
            from prettytable import PrettyTable

            table = PrettyTable(["run_num"] + conditions_to_show)
            for row in values:
                table.add_row(row)
            click.echo(table)
            return
        except ImportError:
            click.echo("# (!) no prettytable module is installed. Using regular table")
            is_dump_view = True

    click.echo("#! {}".format(" ".join(["run_num"].extend(conditions_to_show))))
    for row in values:
        click.echo(" ".join(row))
