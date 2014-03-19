from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
#from werkzeug import check_password_hash, generate_password_hash

#from app import db
#from app.users.forms import RegisterForm, LoginForm
#from app.users.decorators import requires_login

from runconf_db.model import Board, BoardConfiguration, RunConfiguration, BoardInstallation

mod = Blueprint('boards', __name__, url_prefix='/boards')


@mod.route('/')
def index():
    query = g.tdb.session.query(Board).order_by(Board.board_type)
    boards=query.all()
    last_type=None
    boards_by_types ={}
    for board in boards:
        assert (isinstance(board, Board))
        #add new key if there is no one
        if board.board_type not in boards_by_types.keys():
            boards_by_types[board.board_type] = []
        #add board to type
        boards_by_types[board.board_type].append(board)

    return render_template("boards/index.html", boards_by_types=boards_by_types)

@mod.route('/<int:board_id>/in_run/<int:run_number>')
def board_in_run(board_id, run_number):
    """Shows board configuration in urn number"""

    #board = g.tdb.session.query(Board).filter(Board.id == board_id).one()
    board_config = g.tdb.session.query(BoardConfiguration)\
                                .join(BoardConfiguration.runs)\
                                .filter(BoardConfiguration.board_id == board_id,
                                         RunConfiguration.number == run_number)\
                                .one()

    board_install = g.tdb.session.query(BoardInstallation)\
                                 .join(BoardInstallation.runs)\
                                 .filter(RunConfiguration.number == run_number)\
                                 .filter(BoardInstallation.board_id == board_config.board_id)\
                                 .one()
    assert isinstance(board_config, BoardConfiguration)
    assert isinstance(board_install, BoardInstallation)

    board_config.board.board_type
    board_config.board.serial
    board_install.crate.name
    board_install.slot


    #board_config = g.tdb.session.query(BoardConfiguration).all()
    return render_template("boards/board_in_run.html",
                           board_config=board_config,
                           board_install=board_install,
                           run_number=run_number)

@mod.route('/crate/<int:crate_id>/in_run/<int:run_number>')
def crate_in_run(board_id, run_number):
    """Shows board configuration in urn number"""

    #board = g.tdb.session.query(Board).filter(Board.id == board_id).one()
    board_config = g.tdb.session.query(BoardConfiguration)\
                                .join(BoardConfiguration.runs)\
                                .filter(BoardConfiguration.board_id == board_id,
                                         RunConfiguration.number == run_number)\
                                .one()

    board_install = g.tdb.session.query(BoardInstallation)\
                                 .join(BoardInstallation.runs)\
                                 .filter(RunConfiguration.number == run_number)\
                                 .filter(BoardInstallation.board_id == board_config.board_id)\
                                 .one()
    assert isinstance(board_config, BoardConfiguration)
    assert isinstance(board_install, BoardInstallation)

    board_config.board.board_type
    board_config.board.serial
    board_install.crate.name
    board_install.slot


    #board_config = g.tdb.session.query(BoardConfiguration).all()
    return render_template("boards/board_in_run.html",
                           board_config=board_config,
                           board_install=board_install,
                           run_number=run_number)

@mod.route("/info/<int:board_id>")
def info(board_id):
    board = g.tdb.session.query(Board).filter(Board.id == board_id).first()

    return render_template("boards/info.html", board=board)


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
