import click
from rcdb import RCDBProvider

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