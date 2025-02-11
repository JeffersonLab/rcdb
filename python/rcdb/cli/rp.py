# rp.py
import click
import sqlalchemy
from sqlalchemy import select
from sqlalchemy.exc import OperationalError

import rcdb
from rcdb import RCDBProvider
from rcdb.model import RunPeriod
from rcdb.cli.context import pass_rcdb_context

@click.group(invoke_without_command=True)
@click.pass_context
def rp(context):
    """
    Run Periods management commands.

    If invoked without a subcommand, this command lists all run periods.
    """

    connection_str = context.obj.connection_str
    if not connection_str:
        print("ERROR connection string is missing.")
        exit(1)

    if context.invoked_subcommand is not None:
        return

    provider = context.obj.db
    assert isinstance(provider, RCDBProvider)

    session = provider.session
    run_periods = session.query(RunPeriod).order_by(RunPeriod.id.asc()).all()
    if not run_periods:
        print("No run periods found.")
        return

    print_run_periods(run_periods)


@rp.command()
@click.option('--name', required=True, help="Name of the run period, e.g. RunPeriod-2025-01.")
@click.option('--description', default='', help="Description of the run period.")
@click.option('--run-min', 'run_min', required=True, type=int, help="Minimum run number in the period.")
@click.option('--run-max', 'run_max', required=True, type=int, help="Maximum run number in the period.")
@click.option('--start-date', default=None, help="Start date in YYYY-MM-DD format.")
@click.option('--end-date', default=None, help="End date in YYYY-MM-DD format.")
@pass_rcdb_context
def add(context, name, description, run_min, run_max, start_date, end_date):
    """
    Adds a new run period.
    """
    connection_str = context.connection_str
    if not connection_str:
        print("ERROR: No connection string provided.")
        exit(1)

    provider = RCDBProvider()
    provider.connect(connection_str, check_version=False)
    session = provider.session

    # Convert date strings to Date objects if provided
    # You may want to handle exceptions for invalid formats
    s_date = None
    e_date = None

    if start_date:
        try:
            s_date = sqlalchemy.sql.func.DATE(start_date)  # or use datetime.strptime
        except ValueError:
            print(f"ERROR: Invalid start-date format '{start_date}'. Should be YYYY-MM-DD.")
            exit(1)

    if end_date:
        try:
            e_date = sqlalchemy.sql.func.DATE(end_date)
        except ValueError:
            print(f"ERROR: Invalid end-date format '{end_date}'. Should be YYYY-MM-DD.")
            exit(1)

    # Create and insert the new RunPeriod
    new_period = RunPeriod(name=name,
                           description=description,
                           run_min=run_min,
                           run_max=run_max,
                           start_date=start_date,
                           end_date=end_date)
    session.add(new_period)
    session.commit()

    print(f"Added new run period: {new_period}")

@rp.command()
@click.argument('period_id', type=int)
@click.option('--yes', is_flag=True, help="Skip prompt confirmation and remove directly.")
@pass_rcdb_context
def rm(context, period_id, yes):
    """
    Removes a run period by ID.
    """
    connection_str = context.connection_str
    if not connection_str:
        print("ERROR: No connection string provided.")
        exit(1)

    provider = RCDBProvider()
    provider.connect(connection_str, check_version=False)
    session = provider.session

    rp_item = session.query(RunPeriod).filter(RunPeriod.id == period_id).one_or_none()
    if not rp_item:
        print(f"ERROR: Run period with ID={period_id} was not found.")
        exit(1)

    # If user didn't supply --yes, prompt for confirmation
    if not yes:
        if not click.confirm(f"Do you really want to remove run period ID={period_id} ({rp_item.name})?"):
            print("Aborted.")
            return

    session.delete(rp_item)
    session.commit()
    print(f"Removed run period ID={period_id} ({rp_item.name}).")

@rp.command()
@click.argument('period_id', type=int)
@click.option('--name', default=None, help="New name of the run period.")
@click.option('--description', default=None, help="New description of the run period.")
@click.option('--run-min', 'run_min', type=int, default=None, help="New minimum run number.")
@click.option('--run-max', 'run_max', type=int, default=None, help="New maximum run number.")
@click.option('--start-date', default=None, help="New start date in YYYY-MM-DD format.")
@click.option('--end-date', default=None, help="New end date in YYYY-MM-DD format.")
@pass_rcdb_context
def update(context, period_id, name, description, run_min, run_max, start_date, end_date):
    """
    Updates an existing run period by ID.
    """
    connection_str = context.connection_str
    if not connection_str:
        print("ERROR: No connection string provided.")
        exit(1)

    provider = RCDBProvider()
    provider.connect(connection_str, check_version=False)
    session = provider.session

    rp_item = session.query(RunPeriod).filter(RunPeriod.id == period_id).one_or_none()
    if not rp_item:
        print(f"ERROR: Run period with ID={period_id} was not found.")
        exit(1)

    if name is not None:
        rp_item.name = name
    if description is not None:
        rp_item.description = description
    if run_min is not None:
        rp_item.run_min = run_min
    if run_max is not None:
        rp_item.run_max = run_max
    if start_date is not None:
        # You may want to parse and validate the date string similarly as in add()
        rp_item.start_date = start_date
    if end_date is not None:
        rp_item.end_date = end_date

    session.commit()
    print(f"Updated run period ID={period_id}: {rp_item}")

def print_run_periods(run_periods):
    # 1) Gather data strings and compute column widths
    # ------------------------------------------------
    # - We'll measure lengths of the run period's name
    # - We'll measure lengths of the "[run_min-run_max]" string

    # Build a list of rows so we only format once
    rows = []
    for rp_item in run_periods:
        id_str = str(rp_item.id)
        name_str = rp_item.name
        runs_str = f"[{rp_item.run_min}-{rp_item.run_max}]"
        # Dates are fixed width, 23 chars, like "2025-01-30 - 2026-07-30"
        # We'll store the final string but no need to measure it for alignment
        if rp_item.start_date and rp_item.end_date:
            dates_str = f"{rp_item.start_date} - {rp_item.end_date}"
        else:
            # Handle possible missing dates
            start_str = str(rp_item.start_date) if rp_item.start_date else "None"
            end_str = str(rp_item.end_date) if rp_item.end_date else "None"
            dates_str = f"{start_str} - {end_str}"

        description_str = rp_item.description if rp_item.description else ""

        rows.append((id_str, name_str, runs_str, dates_str, description_str))

    # Determine max width for NAME and RUNS
    # (ID is small, and DATES is fixed)
    max_name_width = max(len(row[1]) for row in rows) if rows else 10
    max_runs_width = max(len(row[2]) for row in rows) if rows else 10

    # We'll define a fixed width for DATES as 23
    # (YYYY-MM-DD - YYYY-MM-DD) => 10 + 3 + 10 = 23
    date_width = 23

    # 2) Print the table header
    # -------------------------
    header_id = "ID"
    header_name = "NAME"
    header_runs = "RUNS"
    header_dates = "DATES"
    header_description = "DESCRIPTION"

    # Construct the format string
    # e.g.  ID (left), NAME (left, max_name_width), RUNS (left, max_runs_width),
    #       DATES (left, date_width), DESCRIPTION at the end (no fixed width).
    row_format = (
        f"{{:<3}}  "  # ID has a small width, left aligned
        f"{{:<{max_name_width}}}  "
        f"{{:<{max_runs_width}}}  "
        f"{{:<{date_width}}}  "
        f"{{}}"  # Description no fixed width
    )

    # Print header row
    print(row_format.format(
        header_id,
        header_name,
        header_runs,
        header_dates,
        header_description
    ))

    # Print a separator row
    print(row_format.format(
        "-" * len(header_id),
        "-" * max_name_width,
        "-" * max_runs_width,
        "-" * date_width,
        "-" * len(header_description)
    ))

    # 3) Print all rows
    # -----------------
    for (id_str, name_str, runs_str, dates_str, description_str) in rows:
        print(row_format.format(
            id_str,
            name_str,
            runs_str,
            dates_str,
            description_str
        ))
