import sys
import click

from rcdb.app_context import parse_run_range
from rcdb.cli.context import pass_rcdb_context
from rcdb.provider import RcdbSelectionResult


@click.command(name="select")
@click.argument('query', required=False)
@click.argument('views_or_runs', nargs=-1)
@click.option('--dump', '-d', 'is_dump_view', is_flag=True,
              help='Display results in export-friendly format without borders or extra formatting')
@click.option('--desc/--asc', 'is_descending', default=False,
              help="Sort order of run number descending or ascending")
@click.option("--verbose", "-v", "is_verbose", default=False, is_flag=True, help="Verbose output")
@pass_rcdb_context
def select_command(rcdb_context, query, views_or_runs, is_dump_view, is_descending, is_verbose):
    """Select runs and get their values."""
    db = rcdb_context.require_connected_db()
    args = []
    if query is not None:
        args.append(str(query))
    args.extend([str(v) for v in views_or_runs])
    run_range_str, query, view = _process_sel_args(args)

    run_periods = db.get_run_periods(sort="desc")
    run_min, run_max = parse_run_range(run_range_str, run_periods)


    # No run min or max. But! We use the latest run period
    if run_min is None and run_max is None and run_periods:
        # get the last run period?
        run_min = run_periods[0].run_min
        run_max = run_periods[0].run_max

    if run_min is None:
        run_min = 0
    if run_max is None:
        run_max = sys.maxsize  # Use sys.maxsize in Python 3 instead of sys.maxint

    if query == '@' or query is None:
        query = ''

    if not view:
        view = "event_count run_config"

    if "," in view:
        view = view.replace(",", " ")

    conditions_to_show = view.split()

    if is_verbose:
        print_selection_input(conditions_to_show, query, run_min, run_max, is_descending)
    values = db.select_values(conditions_to_show, query, run_min, run_max, sort_desc=is_descending)

    if is_verbose:
        print_performance(values)

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


def print_selection_input(conditions_to_show, query, run_min, run_max, is_descending):
    print("Conditions to show:", conditions_to_show)
    print(f"Query: {query}")
    print(f"Run range: {run_min} - {run_max}")
    print(f"Order: {'desc' if is_descending else 'asc' }")
    pass

def print_performance(result):
    assert isinstance(result, RcdbSelectionResult)
    print("Query time:")
    print(f"   preparation      : {result.performance['preparation']}")
    print(f"   query            : {result.performance['query']}")
    print(f"   selection        : {result.performance['selection']}")
    print(f"   start_time_stamp : {result.performance['start_time_stamp']}")
    print(f"   total            : {result.performance['total']}")