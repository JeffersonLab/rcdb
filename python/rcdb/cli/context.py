
import click
from rcdb.app_context import RcdbApplicationContext

pass_rcdb_context = click.make_pass_decorator(RcdbApplicationContext)
