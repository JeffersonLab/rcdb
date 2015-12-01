from operator import attrgetter
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
#from werkzeug import check_password_hash, generate_password_hash
import rcdb
from collections import defaultdict

#from app import db
#from app.users.forms import RegisterForm, LoginForm
#from app.users.decorators import requires_login

#from app.users.models import User
from rcdb.model import Run, BoardInstallation

mod = Blueprint('runs', __name__, url_prefix='/runs')


@mod.route('/')
def index():
    runs = g.tdb.session.query(Run).order_by(Run.number.desc()).all()
    return render_template("runs/index.html", runs=runs)
    pass


@mod.route('/info/<int:run_number>')
def info(run_number):
    """Shows run information and statistics"""

    run = g.tdb.session.query(Run).filter(Run.number == run_number).first()
    assert (isinstance(run, Run))

    # create board by crate list
    bi_by_crate = defaultdict(list)
    for bi in run.board_installations:
        bi_by_crate[bi.crate].append(bi)

    # sort boards by slot
    for bis in bi_by_crate.values():
        bis.sort(key=lambda x: x.slot)

    return render_template("runs/info.html",
                           run=run,
                           conditions=run.conditions,
                           board_installs_by_crate=bi_by_crate,)
