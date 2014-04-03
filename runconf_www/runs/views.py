from operator import attrgetter
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
#from werkzeug import check_password_hash, generate_password_hash
import runconf_db
from collections import defaultdict

#from app import db
#from app.users.forms import RegisterForm, LoginForm
#from app.users.decorators import requires_login

#from app.users.models import User
from runconf_db.model import RunConfiguration, BoardInstallation

mod = Blueprint('runs', __name__, url_prefix='/runs')


@mod.route('/')
def index():
    runs = g.tdb.session.query(RunConfiguration).order_by(RunConfiguration.number.desc()).all()
    return render_template("runs/index.html", runs=runs)
    pass


@mod.route('/info/<int:run_number>')
def info(run_number):
    """Shows run information and statistics"""
    run = g.tdb.session.query(RunConfiguration).filter(RunConfiguration.number == run_number).first()
    assert (isinstance(run, RunConfiguration))

    #create board by crate list
    bi_by_crate = defaultdict(list)
    for bi in run.board_installations:
        bi_by_crate[bi.crate].append(bi)

    #sort boards by slot
    for bis in bi_by_crate.values():
        bis.sort(key=lambda x: x.slot)

    return render_template("runs/info.html",
                           run=run,
                           records_map=run.records_map,
                           board_installs_by_crate=bi_by_crate,
                           start_comment_key=runconf_db.START_COMMENT_RECORD_KEY,
                           end_comment_key=runconf_db.END_COMMENT_RECORD_KEY,
                           component_stat_key=runconf_db.COMPONENT_STAT_KEY)



  # @mod.route('/me/')
  # @requires_login
  # def home():
  #   return render_template("users/profile.html", user=g.user)
  #
  # @mod.before_request
  # def before_request():
  #   """
  #   pull user's profile from the database before every request are treated
  #   """
  #   g.user = None
  #   if 'user_id' in session:
  #     g.user = User.query.get(session['user_id'])
  #
  # @mod.route('/login/', methods=['GET', 'POST'])
  # def login():
  #   """
  #   Login form
  #   """
  #   form = LoginForm(request.form)
  #   # make sure data are valid, but doesn't validate password is right
  #   if form.validate_on_submit():
  #     user = User.query.filter_by(email=form.email.data).first()
  #     # we use werzeug to validate user's password
  #     if user and check_password_hash(user.password, form.password.data):
  #       # the session can't be modified as it's signed,
  #       # it's a safe place to store the user id
  #       session['user_id'] = user.id
  #       flash('Welcome %s' % user.name)
  #       return redirect(url_for('users.home'))
  #     flash('Wrong email or password', 'error-message')
  #   return render_template("users/login.html", form=form)
  #
  # @mod.route('/register/', methods=['GET', 'POST'])
  # def register():
  #   """
  #   Registration Form
  #   """
  #   form = RegisterForm(request.form)
  #   if form.validate_on_submit():
  #     # create an user instance not yet stored in the database
  #     user = User(name=form.name.data, email=form.email.data, \
  #       password=generate_password_hash(form.password.data))
  #     # Insert the record in our database and commit it
  #     db.session.add(user)
  #     db.session.commit()
  #
  #     # Log the user in, as he now has an id
  #     session['user_id'] = user.id
  #
  #     # flash will display a message to the user
  #     flash('Thanks for registering')
  #     # redirect user to the 'home' method of the user module.
  #     return redirect(url_for('users.home'))
  #   return render_template("users/register.html", form=form)
