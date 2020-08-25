from rcdb.alias import get_default_aliases_by_name
from rcdb.model import Run
from flask import Flask, render_template, g, request, url_for
import rcdb
from datetime import datetime

# configuration
from sqlalchemy.orm import subqueryload

DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
SQL_CONNECTION_STRING = "mysql+pymysql://rcdb@127.0.0.1/rcdb"

app = Flask(__name__)
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


@app.route('/')
def index():

    # Select the last 50 runs and
    runs = g.tdb.session\
        .query(Run)\
        .order_by(Run.number.desc())\
        .options(subqueryload(Run.conditions))\
        .limit(50)
    condition_types = g.tdb.get_condition_types()

    return render_template("index.html", runs=runs, DefaultConditions=rcdb.DefaultConditions, condition_types=condition_types)


@app.template_filter('remove_dot_conf')
def remove_dot_conf_filter(s):
    """Removes '.conf' at the end of the string
    :type s:str

    """
    return s[:-5] if s.endswith(".conf") else s;

    return s[::-1]


def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)


app.jinja_env.globals['url_for_other_page'] = url_for_other_page
app.jinja_env.globals['rcdb_default_alias'] = rcdb.alias.default_aliases
# register modules
from runs.views import mod as runs_module
from logs.views import mod as logs_module
from files.views import mod as files_module

from statistics.views import mod as statistics_module
from conditions.views import mod as conditions_module


app.register_blueprint(runs_module)
app.register_blueprint(logs_module)
app.register_blueprint(files_module)
app.register_blueprint(statistics_module)
app.register_blueprint(conditions_module)

if __name__ == '__main__':
    app.run()
