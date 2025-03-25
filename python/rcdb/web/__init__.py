import os
from datetime import datetime
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

DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
SQL_CONNECTION_STRING = "mysql+pymysql://rcdb@127.0.0.1/rcdb"

# Get the current directory
current_directory = os.path.dirname(os.path.abspath(__file__))
template_folder=os.path.join(current_directory, 'templates')

# Create Flask app with custom template folder
app = Flask(__name__, template_folder=template_folder)

app.config.from_object(__name__)

@app.before_request
def before_request():
    g.tdb = rcdb.ConfigurationProvider()
    g.tdb.connect(app.config["SQL_CONNECTION_STRING"])
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

app.register_blueprint(runs_module)
app.register_blueprint(logs_module)
app.register_blueprint(files_module)
app.register_blueprint(statistics_module)
app.register_blueprint(conditions_module)
app.register_blueprint(select_values_module)

if __name__ == '__main__':
    app.run()
