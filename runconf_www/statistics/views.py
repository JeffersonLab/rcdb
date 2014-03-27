from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
#from werkzeug import check_password_hash, generate_password_hash

#from app import db
#from app.users.forms import RegisterForm, LoginForm
#from app.users.decorators import requires_login

#from app.users.models import User
from runconf_db.model import LogRecord, RunConfiguration, BoardConfiguration, Crate
from sqlalchemy.sql.expression import desc

mod = Blueprint('statistics', __name__, url_prefix='/statistics')


@mod.route('/')
def index():

    run_count = g.tdb.session.query(RunConfiguration).count()
    run_last = g.tdb.session.query(RunConfiguration).order_by(desc(RunConfiguration.number)).first()
    boards_count = g.tdb.session.query(BoardConfiguration).count()
    crates_count = g.tdb.session.query(Crate).count()

    return render_template("statistics/index.html",
                           run_count=run_count,
                           run_last=run_last,
                           boards_count=boards_count,
                           crates_count=crates_count)
    pass
