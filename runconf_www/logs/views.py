from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
#from werkzeug import check_password_hash, generate_password_hash

#from app import db
#from app.users.forms import RegisterForm, LoginForm
#from app.users.decorators import requires_login

#from app.users.models import User
from runconf_db.model import LogRecord

mod = Blueprint('logs', __name__, url_prefix='/logs')


@mod.route('/')
def index():
    log_records = g.tdb.session.query(LogRecord).order_by(LogRecord.id).limit(100)

    return render_template("logs/index.html", log_records=log_records)
    pass
