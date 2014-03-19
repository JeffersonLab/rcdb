from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
#from werkzeug import check_password_hash, generate_password_hash

#from app import db
#from app.users.forms import RegisterForm, LoginForm
#from app.users.decorators import requires_login

from runconf_db.model import Board, BoardConfiguration, RunConfiguration, BoardInstallation, Crate

mod = Blueprint('crates', __name__, url_prefix='/crates')


@mod.route('/')
def index():
    query = g.tdb.session.query(Crate).order_by(Crate.name)
    crates = query.all()

    return render_template("crates/index.html", crates=crates)

@mod.route('/info/<int:crate_id>')
def info(crate_id):
    crate = g.tdb.session.query(Crate).filter(Crate.id == crate_id).one()


    return render_template("crates/info.html", crate=crate)

