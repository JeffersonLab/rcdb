import click
from .evio_files import evio_files_command


@click.group(name="repair")
def repair_command():
    """ Group of commands that help repair and consolidate RCDB """
    pass


repair_command.add_command(evio_files_command)

