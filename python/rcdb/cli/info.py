import click
import datetime
from .context import pass_rcdb_context
from rcdb.model import Condition, Run, ConfigurationFile, RunPeriod
from .. import ConditionType


@click.command("info", help="Prints summary info about RCDB contents")
@pass_rcdb_context
def info_command(context):
    """
    Shows various summary information about the RCDB database contents.
    """
    db = context.db

    # Number of condition types
    cnd_type_count = db.session.query(ConditionType).count()

    # Number of conditions
    cnd_count = db.session.query(Condition).count()

    # Date-time of the last condition added:
    last_cnd = db.session.query(Condition).order_by(Condition.id.desc()).first()
    cnd_last_time = last_cnd.created if (last_cnd and hasattr(last_cnd, 'created')) else None

    # Number of runs saved
    run_count = db.session.query(Run).count()

    # Number of files saved
    file_count = db.session.query(ConfigurationFile).count()

    # The last 5 runs saved (by run_number DESC)
    last_5_runs = db.session.query(Run).order_by(Run.number.desc()).limit(5).all()

    # The number of run periods saved
    rp_count = db.session.query(RunPeriod).count()

    # 6. The last run period (by ID DESC, or whichever logic you prefer)
    last_rp = db.session.query(RunPeriod).order_by(RunPeriod.id.desc()).first()

    # Print it all
    click.echo(f"Num, condition types: {cnd_type_count}")
    click.echo(f"Num. condition values: {cnd_count}")
    click.echo(f"Last condition date/time: {cnd_last_time}")
    click.echo(f"Number of runs: {run_count}")
    click.echo(f"Number of files: {file_count}")
    click.echo("Last 5 runs saved: " + ", ".join(str(r.number) for r in last_5_runs) if last_5_runs else "No runs")
    click.echo(f"Number of run periods: {rp_count}")
    if last_rp:
        click.echo(f"Last Run Period:")
        click.echo(f"  Name:        {last_rp.name}")
        click.echo(f"  Description: {last_rp.name}")
        click.echo(f"  Run Range:   {last_rp.run_min} - {last_rp.run_max}")
        click.echo(f"  Start Date:  {last_rp.start_date}")
        click.echo(f"  End Date:    {last_rp.end_date}")

    # Finally, show all possible commands (help):
    ctx = click.get_current_context()
    click.echo("\nrun 'rcdb --help' for the list of available commands")

