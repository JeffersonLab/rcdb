from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
#from werkzeug import check_password_hash, generate_password_hash

#from app import db
#from app.users.forms import RegisterForm, LoginForm
#from app.users.decorators import requires_login

#from app.users.models import User
from rcdb.model import LogRecord, Run, SchemaVersion, RunPeriod
from sqlalchemy.sql.expression import desc

mod = Blueprint('statistics', __name__, url_prefix='/statistics')


@mod.route('/')
def index():

    run_count = g.tdb.session.query(Run).count()
    run_last = g.tdb.session.query(Run).order_by(desc(Run.number)).first()
    db_versions = g.tdb.session.query(SchemaVersion).order_by(SchemaVersion.version.desc())
    run_periods = g.tdb.session.query(RunPeriod).order_by(desc(RunPeriod.start_date)).all()

    return render_template("statistics/index.html",
                           run_periods=run_periods,
                           run_count=run_count,
                           run_last=run_last,
                           db_versions=db_versions)
    pass
