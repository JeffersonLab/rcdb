import sys
import click

from rcdb.app_context import parse_run_range
from rcdb import RCDBProvider
from rcdb.cli.context import pass_rcdb_context


def _process_sel_args(args):
    """
    Process the argument list and extract a run range string, query and view.
    :param args: list of user arguments.
    :return: (run_range_str, query, view)
    """
    run_range_str = ''
    for arg in args:
        if '-' in arg:
            run_range_str = arg
            args = [a for a in args if a != arg]
            break

    if len(args) == 0:
        return run_range_str, None, None
    if len(args) == 1:
        return run_range_str, args[0], None

    return run_range_str, args[0], args[1]


@click.command(name="select")
@click.argument('query', required=False)
@click.argument('views_or_runs', nargs=-1)
@click.option('--dump', '-d', 'is_dump_view', is_flag=True,
              help='Display results in export-friendly format without borders or extra formatting')
@click.option('--desc/--asc', '-d/-a', 'is_descending', default=False,
              help="Sort order of run number descending or ascending")
@pass_rcdb_context
def select_command(rcdb_context, query, views_or_runs, is_dump_view, is_descending):
    """Select runs and get their values."""
    assert isinstance(rcdb_context.db, RCDBProvider)
    args = []
    if query is not None:
        args.append(str(query))
    args.extend([str(v) for v in views_or_runs])
    run_range_str, query, view = _process_sel_args(args)

    run_periods = rcdb_context.db.get_run_periods()
    run_min, run_max = parse_run_range(run_range_str, run_periods)

    if run_min is None:
        run_min = 0
    if run_max is None:
        run_max = sys.maxsize  # Use sys.maxsize in Python 3 instead of sys.maxint

    if query == '@' or query is None:
        query = ''

    if not view:
        view = "event_count run_config"

    conditions_to_show = view.split()

    values = rcdb_context.db.select_values([], query, run_min, run_max)

    if not is_dump_view:

        from rich.table import Table
        from rich.console import Console

        console = Console()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("run_num")
        for cond in conditions_to_show:
            table.add_column(cond)
        for row in values:
            table.add_row(*[str(item) for item in row])
        console.print(table)
        return

    # Dump view (export-friendly)
    header = " ".join(["run_num"] + conditions_to_show)
    click.echo("#! " + header)
    for row in values:
        click.echo(" ".join(map(str, row)))
