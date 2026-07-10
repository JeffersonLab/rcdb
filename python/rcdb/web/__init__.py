import logging
import os
from datetime import datetime
from urllib.parse import urlparse

from flask import Flask, render_template, g, request, url_for
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import subqueryload

import rcdb
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

def _resolve_active_database():
    """Pick the connection string for this request and expose selector state.

    Sets ``g.active_db_name`` / ``g.available_databases`` (used by the navbar DB
    selector) and returns the connection string to connect to. Does not touch
    the database -- only reads config and the ``rcdb_database`` cookie.
    """
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

        g.active_db_name = active_name
        g.available_databases = available_dbs
        return available_dbs[active_name]

    # Original single-database behavior
    g.active_db_name = None
    g.available_databases = {}
    return app.config["SQL_CONNECTION_STRING"]


@app.before_request
def before_request():
    # Never gate static assets on the database -- the graceful DB-error page
    # below still needs its CSS/JS to load when the DB is unreachable.
    if request.endpoint == "static":
        return None

    app.jinja_env.globals['datetime_now'] = datetime.now

    # Resolve the selector state first so the navbar (and the DB-error page)
    # can render even if the connection below fails.
    connection_string = _resolve_active_database()

    # Connect fresh, per request. A DB access/connection failure (access
    # denied, too many connections, timeout, host down, ...) must degrade
    # gracefully instead of surfacing a raw 500 -- and must not poison any
    # cookie or cached engine, so a later reload recovers once the DB is back.
    try:
        g.tdb = rcdb.ConfigurationProvider()
        g.tdb.connect(connection_string)
    except SQLAlchemyError:
        return _render_db_error(connection_string)

    return None


def _render_db_error(connection_string):
    """Log the full failure detail and render the sanitized DB-error page.

    The *log* gets everything an admin needs (which database, the underlying
    pymysql/SQLAlchemy error code + message, and the stack trace). The *page*
    gets none of it -- no connection string, host, user, or exception text --
    only a red "DB connection failure" strip with the top menu (and the DB
    selector) intact so the visitor can switch to a working database.
    """
    logger.exception(
        "DB connection/access failure for database '%s' (%s); serving graceful "
        "error page instead of a 500.",
        getattr(g, "active_db_name", None) or "<default>",
        _connection_hint(connection_string),
    )

    # Drop the half-built provider so its engine/pool is released now rather
    # than lingering as a broken cached connection -- the teardown below only
    # disposes fully-connected providers.
    broken = getattr(g, "tdb", None)
    if broken is not None:
        try:
            broken.disconnect()
        except Exception:
            logger.debug("Ignoring error while disposing failed DB engine.",
                         exc_info=True)
        g.tdb = None

    # 503 Service Unavailable: the failure is transient-friendly (e.g. "too
    # many connections" recovers), so signal a retryable condition rather than
    # a 200 or a permanent error. A plain reload after recovery renders fine.
    return render_template("db_error.html"), 503


@app.errorhandler(SQLAlchemyError)
def handle_db_error(error):
    """Catch DB errors raised while a view runs (not just at connect time).

    ``before_request`` already handles the common case (``connect()`` exercises
    the connection via the schema-version check), but a lazily-issued query in
    a view can still raise. Route those through the same graceful page instead
    of a 500. ``g.active_db_name`` / ``g.available_databases`` were set by
    ``before_request`` before the failure, so the selector still renders.
    """
    return _render_db_error(getattr(g.get("tdb", None), "connection_string", ""))


@app.teardown_request
def teardown_request(exception):
    tdb = getattr(g, 'tdb', None)
    if tdb is not None:
        tdb.disconnect()


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')


@app.route('/sample')
def sample():
    return render_template('index.html')


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
