import click
import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table, desc, select
from sqlalchemy.exc import OperationalError

import rcdb
from rcdb import RCDBProvider
from rcdb.model import SchemaVersion, Alias, RunPeriod
from rcdb.cli.context import pass_rcdb_context
from rcdb.provider import stamp_schema_version


@click.group(invoke_without_command=True)
@click.pass_context
def db(ctx):
    """Database management commands."""
    if ctx.invoked_subcommand is None:
        connection_str = ctx.obj.connection_str

        # We create provider manually and not using ctx.obj.db because we need check_version=False
        # We separate class creation and connection because connection_str might be null
        provider = RCDBProvider()
        if not connection_str:
            print("ERROR connection string is missing.")
            exit(1)
        provider.connect(connection_str, check_version=False)
        query = select(SchemaVersion).order_by(SchemaVersion.version.desc())
        schema_version, = provider.session.execute(query).first()
        print("Schema version: {} - '{}'".format(schema_version.version, schema_version.comment))


@db.command()
@pass_rcdb_context
def update(context):
    provider = RCDBProvider(context.connection_str, check_version=False)

    # Check something exists
    if not sqlalchemy.inspect(provider.engine).has_table(SchemaVersion.__tablename__):
        print('The schema version table does not exist. It looks like RCDB v1.')
        current_version = 1
    else:
        print('Found schema version table')
        # Check schema version
        current_version = provider.get_schema_version()

    if current_version != 1:
        print(f"Can't update schema version. Current version is: {current_version.version}. This command can update:")
        print(f"   DB v1 --> v2")
        return
    else:
        print("Found DB v1. Will do v1 --> v2 update")

    # PRINTOUT PART
    print("This command changes RCDB schema in DB")
    click.echo(click.style('(!!!) NEVER EVER RUN THIS ON PRODUCTION DB WITHOUT PRIOR TESTING (!!!)', bold=True))
    print("  -This operation is not done in one transaction. If update fails in the middle, DB will be unusable")
    print("  -Older versions of RCDB clients will not work with new DB schema")
    print("\nDB: {}\n".format(context.connection_str))

    # Double check user knows what will happen
    if not click.confirm('Do you really want to continue?'):
        return

    # That we will need for DB
    metadata = rcdb.model.Base.metadata
    provider = RCDBProvider(context.connection_str, check_version=False)

    # Create alias table
    Alias.__table__.create(provider.engine)

    # Create run periods table
    RunPeriod.__table__.create(provider.engine)

    # List of old tables to drop
    tables_to_drop = [
        'trigger_thresholds',
        'trigger_masks',
        'readout_thresholds',
        'readout_masks',
        'dac_presets',
        'crates',
        'boards',
        'board_installations_have_runs',
        'board_installations',
        'board_configurations_have_runs',
        'board_configurations',
        'alembic_version'
    ]

    with provider.engine.begin() as conn:
        inspector = sqlalchemy.inspect(conn)
        existing_tables = inspector.get_table_names()

        # Drop each table if it is present
        for t in tables_to_drop:
            if t in existing_tables:
                print(f"Dropping table '{t}'")
                conn.execute(sqlalchemy.text(f"DROP TABLE {t}"))

    # Set correct version
    version = stamp_schema_version(provider)
    print("Stamped schema version: {} - '{}'".format(version.version, version.comment))


@db.command()
@click.option('--no-defaults', is_flag=True, help="Don't create default condition types")
@click.option('--drop-all', is_flag=True, help='Drops existing RCDB data if exists')
@click.option('--confirm', is_flag=True, help='For CI automation and tests')
@pass_rcdb_context
def init(context, drop_all, no_defaults, confirm):
    """Database management commands."""

    # PRINTOUT PART
    print("This command creates RCDB schema in DB")
    click.echo(click.style('(!!!) NEVER EVER RUN THIS ON PRODUCTION DB (!!!)', bold=True))
    if drop_all:
        print("--drop-all given ALL RCDB DATA WILL BE REMOVED")
    else:
        print("This command WILL disrupt data if already exists. Use --drop-all flag to clear things first ")
    print("\nDB: {}\n".format(context.connection_str))

    # Double check user knows what will happen
    if not confirm and not click.confirm('Do you really want to continue?'):
        return

    # That we will need for DB
    metadata = rcdb.model.Base.metadata
    provider = RCDBProvider(context.connection_str, check_version=False)

    # Drop all if needed
    if drop_all:
        try:
            metadata.drop_all(provider.engine)
            print("Dropped existing RCDB data")
        except OperationalError as ex:
            print("destroy_schema dropped OperationalError '{}'\nConsidering DB is empty".format(ex))

    # Check something exists
    if sqlalchemy.inspect(provider.engine).has_table(SchemaVersion.__tablename__):
        print('The schema version table exists.')
        print('Use --drop-all flag to clear existing data first')
        return
    else:
        print('The schema version table does not exist.')

    # CREATE ALL TABLES
    rcdb.model.Base.metadata.create_all(provider.engine)
    print("Created RCDB schema")

    # Set correct version
    version = stamp_schema_version(provider)
    print("Stamped schema version: {} - '{}'".format(version.version, version.comment))

    if no_defaults:
        print("--no-defaults flag is given. Skipping creation of default conditions")
    else:
        rcdb.create_default_condition_types(provider)
        print("Created default conditions")
