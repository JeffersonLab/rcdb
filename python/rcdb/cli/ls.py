import click

from rcdb.provider import RCDBProvider
from .context import pass_rcdb_context


@click.command()
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