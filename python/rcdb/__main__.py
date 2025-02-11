# This is the same as rcdb.cli.api:rcdb_cli
# The logic to have it here, is that if one uses:
# python -m rcdb - it works like 'rcdb' command

from rcdb.cli.app import rcdb_cli

rcdb_cli(prog_name="rcdb")
