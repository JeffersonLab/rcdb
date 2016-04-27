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
    """'rcdb' is a command line tool that showcases how to build complex
    command line interfaces with Click.

    This tool is supposed to look like a distributed version control
    system to show how something like this can be structured.
    """
    # Create a repo object and remember it as as the context object.  From
    # this point onwards other commands can refer to it by using the
    # @pass_repo decorator.
    ctx.obj = RcdbApplicationContext(os.path.abspath(user_config), connection)
    ctx.obj.verbose = verbose
    for key, value in config:
        ctx.obj.set_config(key, value)


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
@click.argument('query')
@click.argument('views_or_runs', nargs=-1)
#@click.option('--long', '-l', 'is_long', is_flag=True, help='Prints condition full information')
@pass_rcdb_context
def sel(rcdb_context, query, views_or_runs):
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

    values = rcdb_context.db.select_runs(query, run_min, run_max).get_values(conditions_to_show, True)
    print values


@cli.command()
@click.argument('query')
@click.argument('views_or_runs', nargs=-1)
# @click.option('--long', '-l', 'is_long', is_flag=True, help='Prints condition full information')
@pass_rcdb_context
def plot(rcdb_context, query, views_or_runs):
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

    values = rcdb_context.db.select_runs(query, run_min, run_max).get_values(conditions_to_show, True)
    x_col = [v[0] for v in values]
    y_col = [v[1] for v in values]

    import matplotlib.pyplot as plt
    plt.plot(x_col, y_col,"ro")
    #plt.axis([0, 6, 0, 20])
    plt.show()

def cfg():
    pass


#@cli.command()
@click.argument('src')
@click.argument('dest', required=False)
@click.option('--shallow/--deep', default=False,
              help='Makes a checkout shallow or deep.  Deep by default.')
@click.option('--rev', '-r', default='HEAD',
              help='Clone a specific revision instead of HEAD.')
@pass_rcdb_context
def clone(repo, src, dest, shallow, rev):
    """Clones a repository.

    This will clone the repository at SRC into the folder DEST.  If DEST
    is not provided this will automatically use the last path component
    of SRC and create that folder.
    """
    if dest is None:
        dest = posixpath.split(src)[-1] or '.'
    click.echo('Cloning repo %s to %s' % (src, os.path.abspath(dest)))
    repo.home = dest
    if shallow:
        click.echo('Making shallow checkout')
    click.echo('Checking out revision %s' % rev)


#@cli.command()
@click.confirmation_option()
@pass_rcdb_context
def delete(repo):
    """Deletes a repository.

    This will throw away the current repository.
    """
    click.echo('Destroying repo %s' % repo.home)
    click.echo('Deleted!')


#@cli.command()
@click.option('--username', prompt=True,
              help='The developer\'s shown username.')
@click.option('--email', prompt='E-Mail',
              help='The developer\'s email address')
@click.password_option(help='The login password.')
@pass_rcdb_context
def setuser(repo, username, email, password):
    """Sets the user credentials.

    This will override the current user config.
    """
    repo.set_config('username', username)
    repo.set_config('email', email)
    repo.set_config('password', '*' * len(password))
    click.echo('Changed credentials.')


#@cli.command()
@click.option('--message', '-m', multiple=True,
              help='The commit message.  If provided multiple times each '
              'argument gets converted into a new line.')
@click.argument('files', nargs=-1, type=click.Path())
@pass_rcdb_context
def commit(repo, files, message):
    """Commits outstanding changes.

    Commit changes to the given files into the repository.  You will need to
    "repo push" to push up your changes to other repositories.

    If a list of files is omitted, all changes reported by "repo status"
    will be committed.
    """
    if not message:
        marker = '# Files to be committed:'
        hint = ['', '', marker, '#']
        for file in files:
            hint.append('#   U %s' % file)
        message = click.edit('\n'.join(hint))
        if message is None:
            click.echo('Aborted!')
            return
        msg = message.split(marker)[0].rstrip()
        if not msg:
            click.echo('Aborted! Empty commit message')
            return
    else:
        msg = '\n'.join(message)
    click.echo('Files to be committed: %s' % (files,))
    click.echo('Commit message:\n' + msg)


#@cli.command(short_help='Copies files.')
@click.option('--force', is_flag=True,
              help='forcibly copy over an existing managed file')
@click.argument('src', nargs=-1, type=click.Path())
@click.argument('dst', type=click.Path())
@pass_rcdb_context
def copy(repo, src, dst, force):
    """Copies one or multiple files to a new location.  This copies all
    files from SRC to DST.
    """
    for fn in src:
        click.echo('Copy from %s -> %s' % (fn, dst))






if __name__ == '__main__':
    cli(prog_name="rcdb")
