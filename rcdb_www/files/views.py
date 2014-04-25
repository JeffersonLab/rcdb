from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from rcdb.model import ConfigurationFile
#from werkzeug import check_password_hash, generate_password_hash

#from app import db
#from app.users.forms import RegisterForm, LoginForm
#from app.users.decorators import requires_login

#from app.users.models import User
mod = Blueprint('files', __name__, url_prefix='/files')


@mod.route('/')
def index():
    return render_template("files/index.html", parm="hahaha")
    pass

@mod.route('/info/<int:file_db_id>')
def info(file_db_id):
    #try:
        file = g.tdb.session.query(ConfigurationFile).filter(ConfigurationFile.id == file_db_id).one()
        return render_template("files/info.html", file=file)
    # except:
    #     return render_template("files/not_found.html", id=file_db_id)
    # pass