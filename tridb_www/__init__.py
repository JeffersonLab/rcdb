__author__ = 'romanov'
from flask import Flask, render_template, g


import trigger_db
from trigger_db import Board

# configuration
DATABASE = 'flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'


app = Flask(__name__)
#app.config.from_object('config')
app.config.from_object(__name__)

@app.before_request
def before_request():
    g.tdb = trigger_db.ConfigurationProvider()
    g.tdb.connect()

@app.teardown_request
def teardown_request(exception):
    #tdb = getattr(g, 'db', None)
    pass


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')

@app.route('/sample')
def sample():
    return render_template('index.html')

@app.route('/')
def index():
    return render_template('index.html')

#from  import mod as boardsModule
from boards.views import mod as boards_module
from runs.views import mod as runs_module
from logs.views import mod as logs_module

app.register_blueprint(boards_module)
app.register_blueprint(runs_module)
app.register_blueprint(logs_module)


if __name__ == '__main__':
    app.run()