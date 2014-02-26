from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
#from werkzeug import check_password_hash, generate_password_hash

#from app import db
#from app.users.forms import RegisterForm, LoginForm
#from app.users.decorators import requires_login

#from app.users.models import User
mod = Blueprint('logs', __name__, url_prefix='/logs')


@mod.route('/')
def index():
    return render_template("logs/index.html", parm="hahaha")
    pass
