from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
#from werkzeug import check_password_hash, generate_password_hash

#from app import db
#from app.users.forms import RegisterForm, LoginForm
#from app.users.decorators import requires_login

#from app.users.models import User
from rcdb.model import LogRecord, Run, SchemaVersion
from sqlalchemy.sql.expression import desc

mod = Blueprint('statistics', __name__, url_prefix='/statistics')


@mod.route('/')
def index():

    run_count = g.tdb.session.query(Run).count()
    run_last = g.tdb.session.query(Run).order_by(desc(Run.number)).first()
    boards_count = 0
    crates_count = 0
    db_versions = g.tdb.session.query(SchemaVersion).order_by(SchemaVersion.version.desc())

    return render_template("statistics/index.html",
                           run_count=run_count,
                           run_last=run_last,
                           boards_count=boards_count,
                           crates_count=crates_count,
                           db_versions=db_versions)
    pass
