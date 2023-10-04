import json
import re
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
# from werkzeug import check_password_hash, generate_password_hash
import rcdb
from collections import defaultdict
from rcdb.model import Run, Condition, ConditionType
from sqlalchemy.orm import subqueryload

mod = Blueprint('test_conditions', __name__, url_prefix='/test_conditions')


@mod.route('/')
def index():
    conditions = g.tdb.session.query(ConditionType).order_by(ConditionType.name.asc()).all()
    return render_template("test_conditions/index.html", conditions=conditions)
    pass
