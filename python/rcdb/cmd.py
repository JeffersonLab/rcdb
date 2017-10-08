import os
import sys
import posixpath
import click

from rcdb.app_context import RcdbApplicationContext, parse_run_range
from rcdb import RCDBProvider
from rcdb.model import ConfigurationFile

pass_rcdb_context = click.make_pass_decorator(RcdbApplicationContext)


def get_default_config_path():
    return os.path.join(os.path.expanduser('~'), '.rcdb_user')


@click.group()
@click.option('--user-config', envvar='RCDB_USER_CONFIG', default=get_default_config_path,
              metavar='PATH', help='Changes the user config location.')
@click.option('--connection', '-c', envvar='RCDB_CONNECTION', help='Database connection string',
              default=None, required=True)

@click.option('--config', nargs=2, multiple=True,
              metavar='KEY VALUE', help='Overrides a config key/value pair.')
@click.option('--verbose', '-v', is_flag=True, help='Enables verbose mode.')
@click.version_option('1.0')
@click.pass_context
def cli(ctx, user_config, connection, config, verbose):
    """'rcdb' is a RCDB (run conditions database) command line tool
    This tool allows to select runs and get values as well as manage RCDB values
    """

    # Create a rcdb_app_context object and remember it as as the context object.  From
    # this point onwards other commands can refer to it by using the
    # @pass_rcdb_context decorator.
    ctx.obj = RcdbApplicationContext(os.path.abspath(user_config), connection)
    ctx.obj.verbose = verbose
    for key, value in config:
        ctx.obj.set_config(key, value)


@cli.command()
@click.argument('search', required=False)
@click.option('--long', '-l', 'is_long', is_flag=True, help='Prints condition full information')
@pass_rcdb_context
def ls(context, search, is_long):
    """Lists conditions"""
    db = context.db
    assert isinstance(db, RCDBProvider)
    cnd_types = db.get_condition_types_by_name()
    names = sorted(cnd_types.keys())
    if search:
        names = [n for n in names if search in n]

    longest_len = len(max(names, key=len))
    for name in names:
        cnd_type = cnd_types[name]
        click.echo("{0:<{1}}   {2}".format(name, longest_len, cnd_type.description))


@cli.command()
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



@cli.command()
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

# @cli.command()
# @click.argument('query')
# @click.argument('views_or_runs', nargs=-1)
# # @click.option('--long', '-l', 'is_long', is_flag=True, help='Prints condition full information')
# @pass_rcdb_context
# def plot(rcdb_context, query, views_or_runs):
#     """ Command allows to select runs and get values from it"""
#     assert isinstance(rcdb_context.db, RCDBProvider)
#     args = [str(query)]
#     args.extend([str(v) for v in views_or_runs])
#     run_range_str, query, view = _process_sel_args(args)
#
#     (run_min, run_max) = parse_run_range(run_range_str, rcdb_context.db.get_run_periods())
#
#     if run_min is None:
#         run_min = 0
#
#     if run_max is None:
#         run_max = sys.maxint
#
#     if query == '@' or query is None:
#         query = ''
#
#     if not view:
#         view = "event_count run_config"
#
#     conditions_to_show = view.split()
#
#     try:
#         import matplotlib.pyplot as plt
#
#         values = rcdb_context.db.select_runs(query, run_min, run_max).get_values(conditions_to_show, True)
#         x_col = [v[0] for v in values]
#         plot_data = [x_col, [v[1] for v in values], "ro"]
#
#         plt.plot(*plot_data, label=conditions_to_show[0])
#         plt.show()
#     except ImportError:
#         print("matplotlib library is not found. It is required for 'plot' command. ")


if __name__ == '__main__':
    cli(prog_name="rcdb")