import click
from rcdb import RCDBProvider
import sys

class RcdbApplicationContext(object):

    def __init__(self, home, connection_str):
        self.home = home
        self.db = RCDBProvider(connection_str)
        self.config = {}
        self.verbose = False
        self.connection_str = connection_str

    def set_config(self, key, value):
        self.config[key] = value
        if self.verbose:
            click.echo('  config[%s] = %s' % (key, value), file=sys.stderr)

    def __repr__(self):
        return '<Repo %r>' % self.home


class RcdbAdminApplicationContext(RcdbApplicationContext):

    def __init__(self, home, connection_str):
        super(RcdbAdminApplicationContext).__init__(home, connection_str)



def parse_run_range(run_range_str, run_periods=None):
    """ Parses run range, returning a pair (run_from, run_to) or (run_from, None) or (None, None)

    Function doesn't raise FormatError
    :exception ValueError: if run_range_str is not str

    :param run_range_str: string to parse
    :return: (run_from, run_to). Function always return lower run number as run_from
    """

    if run_range_str is None:
        return None, None

    run_range_str = str(run_range_str).strip()
    if not run_range_str:
        return None, None

    assert isinstance(run_range_str, str)

    # Is it run period?
    if run_periods:
        if run_range_str in run_periods:
            run_min, run_max, descr = run_periods[run_range_str]
            return run_min, run_max

    # Have run-range?
    if '-' in run_range_str:
        tokens = [t.strip() for t in run_range_str.split("-")]
        try:
            run_from = int(tokens[0])
        except (ValueError, KeyError):
            return None, None

        try:
            run_to = int(tokens[1])
        except (ValueError, KeyError):
            return run_from, None

        return (run_from, run_to) if run_from <= run_to else (run_to, run_from)

    # Have run number?
    if run_range_str.isdigit():
        return int(run_range_str), None

    # Default return is index
    return None, None