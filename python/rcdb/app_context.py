import click
from rcdb import RCDBProvider
import sys


class RcdbApplicationContext(object):

    def __init__(self, home, connection_str):
        self.home = home
        self._db_instance = None

        self.config = {}
        self.verbose = False
        self.connection_str = connection_str

    @property
    def db(self) -> RCDBProvider:
        if not self._db_instance:
            self._db_instance = RCDBProvider(self.connection_str)
        return self._db_instance

    def close(self):
        """Disconnect the database if one was opened.

        Safe to call when no connection was ever made. The CLI registers this on
        the Click context so the engine is disposed deterministically when the
        command finishes, instead of waiting for garbage collection (which on
        Python 3.13+ leaks a ``ResourceWarning: unclosed database``).
        """
        if self._db_instance is not None:
            self._db_instance.disconnect()
            self._db_instance = None

    def require_connected_db(self) -> RCDBProvider:
        """Return the RCDBProvider, or fail with a clear CLI error if no connection was given.

        Commands that cannot do anything without a database call this instead of
        using ``db`` directly: a missing connection then produces a clean error
        message rather than crashing later on a ``None`` session. Commands that can
        run without a connection (e.g. ``web`` with ``--add-db``) keep using ``db``.
        """
        if not self.connection_str:
            raise click.UsageError(
                "No connection provided! Provide a DB connection string via the "
                "-c/--connection option or the RCDB_CONNECTION environment variable."
            )
        return self.db

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


def minmax_run_range(run_range: tuple):
    """If one or both values of run_range tuple is None, replaces it to 0 or sys.maxsize

    > minmax_run_range((None, None)) 
    (0, sys.maxsize)
    > minmax_run_range((None, value2)) 
    (0, value2)
    > minmax_run_range((value1, None)) 
    (value1, sys.maxsize)
    > minmax_run_range((value1, value2)) 
    (value1, value2)
    """

    min_run = 0 if run_range[0] is None else run_range[0]
    max_run = sys.maxsize if run_range[1] is None else run_range[1]
    return min_run, max_run
