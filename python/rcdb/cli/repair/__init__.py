import click
from . import evio_files

@click.group()
def repair():
    """
    Group of commands that help repair and consolidate RCDB
    """
    pass

repair.add_command(evio_files.evio_files)