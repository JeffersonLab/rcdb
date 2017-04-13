import os
import sys
import posixpath

import click

from rcdb.app_context import RcdbApplicationContext, parse_run_range
from rcdb import RCDBProvider

pass_rcdb_context = click.make_pass_decorator(RcdbApplicationContext)


def get_default_config_path():
    return os.path.join(os.path.expanduser('~'), '.rcdb_user')


@click.group()
@click.option('--user-config', envvar='RCDB_USER_CONFIG', default=get_default_config_path, metavar='PATH', help='Changes the user config location.')
@click.option('--connection', '-c', envvar='RCDB_CONNECTION', help='Database connection string', default=None, required=True)
@click.option('--config', nargs=2, multiple=True, metavar='KEY VALUE', help='Overrides a config key/value pair.')
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


@cli.command(help="")
@click.argument('search', required=False)
@click.option('--long', '-l', 'is_long', is_flag=True, help='Prints condition full information')
@pass_rcdb_context
def walk(context, search, is_long):
    """Lists condition


    """
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
@click.argument('search', required=False)
@click.option('--long', '-l', 'is_long', is_flag=True, help='Prints condition full information')
@pass_rcdb_context
def ls(context, search, is_long):
    """Lists condition


    """
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







if __name__ == '__main__':
    cli(prog_name="rcdb")