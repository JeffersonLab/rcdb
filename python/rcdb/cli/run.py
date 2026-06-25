import click

from rcdb.provider import RCDBProvider
from rcdb.model import ConfigurationFile
from .context import pass_rcdb_context


# Maximum number of characters shown for a condition value.
_MAX_VALUE_LEN = 50


def format_condition_value(value):
    """Flatten a condition value to a single line and truncate it.

    New lines are replaced by spaces and the result is cut to the first
    ``_MAX_VALUE_LEN`` characters, appending ``...`` when truncation happened.
    """
    text = str(value).replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    if len(text) > _MAX_VALUE_LEN:
        return text[:_MAX_VALUE_LEN] + "..."
    return text


@click.command(name="run")
@click.argument("run_number", type=int)
@click.option("-i", "--info", "show_info", is_flag=True, default=False,
              help="Show only the run info line (start - end).")
@click.option("-c", "--conditions", "show_conditions", is_flag=True, default=False,
              help="Show only conditions (without the CONDITIONS title).")
@click.option("-f", "--files", "show_files", is_flag=True, default=False,
              help="Show only files (without the FILES title).")
@pass_rcdb_context
def run_command(context, run_number, show_info, show_conditions, show_files):
    """Show information about a single run: its time span, conditions and files.

    `rcdb <run number>` is a shortcut for `rcdb run <run number>`.

    With no -i/-c/-f flag the full report is printed. Passing one or more flags
    limits the output to just those sections (and drops the section titles).
    """
    db = context.require_connected_db()
    assert isinstance(db, RCDBProvider)

    run = db.get_run(run_number)
    if not run:
        click.echo("Run {} is not found in DB.".format(run_number), err=True)
        raise click.Abort()

    # No flag => full report with titles. Any flag => only those sections.
    full = not (show_info or show_conditions or show_files)

    # ---- Info -----------------------------------------------------------
    if full or show_info:
        start = run.start_time if run.start_time is not None else "?"
        end = run.end_time if run.end_time is not None else "?"
        click.echo("Run {}: {} - {}".format(run.number, start, end))

    # ---- Conditions -----------------------------------------------------
    if full or show_conditions:
        if full:
            click.echo("")
            click.echo("CONDITIONS:")
        conditions = sorted(run.conditions, key=lambda c: c.name)
        if conditions:
            for condition in conditions:
                click.echo("   {} - {}".format(condition.name, format_condition_value(condition.value)))
        elif full:
            click.echo("   (none)")

    # ---- Files ----------------------------------------------------------
    if full or show_files:
        important = sorted(f.path for f in run.files
                           if f.importance == ConfigurationFile.IMPORTANCE_HIGH)
        other = sorted(f.path for f in run.files
                       if f.importance != ConfigurationFile.IMPORTANCE_HIGH)

        if full:
            click.echo("FILES")
        click.echo("   important:")
        for path in important:
            click.echo("        {}".format(path))
        click.echo("   other files:")
        for path in other:
            click.echo("        {}".format(path))
