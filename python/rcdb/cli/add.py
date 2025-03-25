import click
from rcdb.provider import RCDBProvider
from rcdb.model import ConditionType, ConfigurationFile
from rcdb.cli.context import pass_rcdb_context
from rcdb import ConditionType as CT

# A helper mapping from short strings like 'bool','int','float' -> ConditionType.<XYZ>_FIELD
TYPE_MAP = {
    "bool": CT.BOOL_FIELD,
    "int": CT.INT_FIELD,
    "float": CT.FLOAT_FIELD,
    "string": CT.STRING_FIELD,
    "json": CT.JSON_FIELD,
    "time": CT.TIME_FIELD,
    "blob": CT.BLOB_FIELD
}


@click.group("add", help="Add data to the RCDB (types, conditions, files).")
@pass_rcdb_context
def add_command(context):
    """
    The 'add' group command. See subcommands like:
      rcdb add type - adds Condition Type
      rcdb add condition - adds Condition to a run
      rcdb add file - adds File and associate it to a run
    """
    pass


@add_command.command(name="type", help="Add a new condition type to the DB.")
@click.argument("name", required=True)
@click.option("--type", "value_type",
              type=click.Choice(TYPE_MAP.keys(), case_sensitive=False),
              default="float", show_default=True,
              help="Data type of the condition (bool, int, float, string, json, time, blob).")
@click.option("--description", "-d",
              default="",
              help="Optional description.")
@pass_rcdb_context
def add_type(context, name, value_type, description):
    """
    Adds a new condition type with given NAME and --type/--description.

    Example:
      rcdb add type beam_current --type=float --description "Beam current in nA"
    """
    db = context.db
    actual_type = TYPE_MAP[value_type.lower()]

    # Create or verify
    click.echo(f"Creating condition type '{name}' of type '{value_type}'")
    ct = db.create_condition_type(name, actual_type, description)
    click.echo("Done.")


@add_command.command(name="condition", help="Add or update a condition for a run.")
@click.argument("run_number", type=int)
@click.argument("condition_name", type=str)
@click.argument("value", required=True)
@click.option("--replace", "-r", is_flag=True,
              help="If present, replace existing value if it already exists.")
@pass_rcdb_context
def add_condition(context, run_number, condition_name, value, replace):
    """
    Adds a condition to RUN_NUMBER called CONDITION_NAME with given VALUE.

    Example:
      rcdb add condition 1000 my_value 123.4
      rcdb add condition 1000 event_count 10000 --replace
    """
    db = context.db

    # 1) Ensure run exists
    run = db.get_run(run_number)
    if not run:
        run = db.create_run(run_number)
        click.echo(f"Created new run #{run_number}")

    # 2) Look up condition type
    try:
        condition_type = db.get_condition_type(condition_name)
    except:
        click.echo(f"ERROR: No condition type '{condition_name}' found in DB. Create it first with:\n"
                   f"  rcdb add type {condition_name} --type=<type>\n", err=True)
        raise click.Abort()

    # 3) Convert value if needed
    #    (If 'value' is obviously numeric, you can do more advanced type conversion here if you like)
    #    For now we store the raw string and rely on ConditionType conversion in RCDB:
    #    db.add_condition will do the right thing (if you pass an int for an INT_FIELD, float for FLOAT_FIELD, etc.)
    #    You might do a quick parse though, e.g. if condition_type.value_type is CT.FLOAT_FIELD => float(value), etc.

    # 4) Add condition
    db.add_condition(run, condition_type, value, replace=replace)
    db.session.commit()
    click.echo(f"Added condition '{condition_name}' = '{value}' to run {run_number}")


@add_command.command(name="file", help="Attach or add a file to a run in the DB.")
@click.argument("run_number", type=int)
@click.argument("file_path", type=str)
@click.option("--importance", "-i", default=0, type=int,
              help="Importance level, default=0 (lowest).")
@click.option("--overwrite", is_flag=True, default=False,
              help="Overwrite existing content for the same path & run.")
@click.option("--content", default=None,
              help="Optional raw content to store. If not specified, reads from file_path on disk.")
@pass_rcdb_context
def add_file(context, run_number, file_path, importance, overwrite, content):
    """
    Adds or attaches a configuration file to RUN_NUMBER using FILE_PATH.

    Example:
      rcdb add file 1000 /path/to/coda_run.log
      rcdb add file 1000 /path/to/config.txt --importance=2 --overwrite
    """
    db = context.db
    run = db.get_run(run_number)
    if not run:
        run = db.create_run(run_number)
        click.echo(f"Created new run #{run_number}")

    if content:
        # If user provides --content, we do not read from the file path.
        # We'll just store the provided content under that path.
        the_content = content
        click.echo("Using the provided --content instead of reading from disk.")
    else:
        # Otherwise read from disk
        try:
            with open(file_path, "r") as f:
                the_content = f.read()
        except Exception as ex:
            click.echo(f"ERROR: Cannot open/read file '{file_path}': {ex}", err=True)
            raise click.Abort()

    # Now add
    db.add_configuration_file(run, file_path, content=the_content, overwrite=overwrite, importance=importance)
    db.session.commit()
    click.echo(f"File '{file_path}' attached to run {run_number}.")
