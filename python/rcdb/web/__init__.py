import logging
import os
from datetime import datetime
from urllib.parse import urlparse

from flask import Flask, render_template, g, request, url_for
from sqlalchemy.orm import subqueryload

import rcdb
from rcdb.alias import get_default_aliases_by_name
from rcdb.model import Run, RunPeriod

# register modules
from rcdb.web.modules import runs_module
from rcdb.web.modules import logs_module
from rcdb.web.modules import files_module
from rcdb.web.modules import statistics_module
from rcdb.web.modules import conditions_module
from rcdb.web.modules import select_values_module

logger = logging.getLogger(__name__)

DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
SQL_CONNECTION_STRING = "mysql+pymysql://rcdb@127.0.0.1/rcdb"
AVAILABLE_DATABASES = {}   # dict of {"name": "connection_string", ...}
DEFAULT_DATABASE = ""       # connection string used as default


def _connection_hint(conn_str):
    """Extract a short hint from a SQLAlchemy connection string.

    Examples:
        "mysql+pymysql://rcdb@127.0.0.1/rcdb" -> "rcdb@127.0.0.1"
        "sqlite:///path/to/file.db"            -> "file.db"
    """
    try:
        parsed = urlparse(conn_str)
        if parsed.scheme.startswith("sqlite"):
            # For sqlite, show just the filename
            path = parsed.path.lstrip("/")
            return os.path.basename(path) if path else conn_str
        # For mysql/postgres etc, show user@host
        host = parsed.hostname or ""
        user = parsed.username or ""
        if user:
            return f"{user}@{host}"
        return host or conn_str
    except Exception:
        return conn_str

# Get the current directory
current_directory = os.path.dirname(os.path.abspath(__file__))
template_folder=os.path.join(current_directory, 'templates')

# Create Flask app with custom template folder
app = Flask(__name__, template_folder=template_folder)

app.config.from_object(__name__)

@app.before_request
def before_request():
    available_dbs = app.config.get("AVAILABLE_DATABASES", {})

    if available_dbs:
        # Determine which database to connect to
        cookie_db = request.cookies.get("rcdb_database", "")
        default_conn = app.config.get("DEFAULT_DATABASE", "")

        if cookie_db and cookie_db in available_dbs:
            # Cookie points to a valid database
            active_name = cookie_db
        elif default_conn:
            # Find name for the default connection string
            active_name = None
            for name, conn in available_dbs.items():
                if conn == default_conn:
                    active_name = name
                    break
            if active_name is None:
                # DEFAULT_DATABASE not in AVAILABLE_DATABASES
                active_name = next(iter(available_dbs))
                logger.warning(
                    "DEFAULT_DATABASE '%s' is not in AVAILABLE_DATABASES, "
                    "using '%s' instead.", default_conn, active_name
                )
        else:
            # No default set, use first available
            active_name = next(iter(available_dbs))

        connection_string = available_dbs[active_name]
        g.active_db_name = active_name
        g.available_databases = available_dbs
    else:
        # Original single-database behavior
        connection_string = app.config["SQL_CONNECTION_STRING"]
        g.active_db_name = None
        g.available_databases = {}

    g.tdb = rcdb.ConfigurationProvider()
    g.tdb.connect(connection_string)
    app.jinja_env.globals['datetime_now'] = datetime.now


@app.teardown_request
def teardown_request(exception):
    tdb = getattr(g, 'db', None)
    if tdb:
        tdb.close()


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')


@app.route('/sample')
def sample():
    return render_template('index.html')


@app.route('/run_periods')
def run_periods():
    run_periods = g.tdb.session.query(RunPeriod).all()


@app.route('/')
def index():
    # Find the latest run period based on `end_date` (or use `id` if more appropriate)
    latest_run_period = g.tdb.session.query(RunPeriod).order_by(RunPeriod.end_date.desc()).first()

    runs_query =  g.tdb.session \
            .query(Run) \
            .order_by(Run.number.desc())

    if latest_run_period:
        runs_query = runs_query.filter(
            Run.number >= latest_run_period.run_min,
            Run.number <= latest_run_period.run_max)

    runs = runs_query.options(subqueryload(Run.conditions)).limit(50)

    condition_types = g.tdb.get_condition_types()

    return render_template("index.html",
                           runs=runs,
                           DefaultConditions=rcdb.DefaultConditions,
                           condition_types=condition_types)


@app.template_filter('remove_dot_conf')
def remove_dot_conf_filter(s):
    """Removes '.conf' at the end of the string
    :type s:str

    """
    return s[:-5] if s.endswith(".conf") else s


def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)


app.jinja_env.globals['url_for_other_page'] = url_for_other_page
app.jinja_env.globals['rcdb_default_alias'] = rcdb.alias.default_aliases
app.jinja_env.globals['connection_hint'] = _connection_hint

app.register_blueprint(runs_module)
app.register_blueprint(logs_module)
app.register_blueprint(files_module)
app.register_blueprint(statistics_module)
app.register_blueprint(conditions_module)
app.register_blueprint(select_values_module)

if __name__ == '__main__':
    app.run()
