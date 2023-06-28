import click
import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table, desc, select
from sqlalchemy.exc import OperationalError

import rcdb
from rcdb import RCDBProvider
from rcdb.model import SchemaVersion
from rcdb.rcdb_cli.context import pass_rcdb_context
from rcdb.provider import stamp_schema_version

@click.group(invoke_without_command=True)
@click.pass_context
def db(ctx):
    """Database management commands."""
    if ctx.invoked_subcommand is None:
        connection_str = ctx.obj.connection_str
        provider = RCDBProvider(connection_str, check_version=False)
        schema_version, = provider.session.execute(select(SchemaVersion).order_by(SchemaVersion.version.desc())).first()
        print("Schema version: {} - '{}'".format(schema_version.version, schema_version.comment))


# add a command to the 'db' group
@db.command()
@click.option("--connection", help="The connection string for the database.")
@click.option("--connection", help="The connection string for the database.")
def update(connection):
    """Update the database schema."""
    engine = create_engine(connection)
    metadata = MetaData()
    # Perform your database operations here...
    # For example, load a table from the database or create it if it doesn't exist
    users = Table('users', metadata, autoload_with=engine, extend_existing=True)
    # ...


@db.command()
@click.option('--drop-all', is_flag=True, help='Drops existing RCDB data if exists')
@pass_rcdb_context
def init(context, drop_all):
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
    if not click.confirm('Do you really want to continue?'):
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
