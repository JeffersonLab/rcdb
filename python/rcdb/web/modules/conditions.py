from flask import Blueprint, render_template, g
# from werkzeug import check_password_hash, generate_password_hash
from rcdb.model import ConditionType

mod = Blueprint('conditions', __name__, url_prefix='/conditions')


@mod.route('/')
def index():
    conditions = g.tdb.session.query(ConditionType).order_by(ConditionType.name.asc()).all()
    return render_template("conditions/index.html", conditions=conditions)
    pass

