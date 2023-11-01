import json
import re
import sys

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
# from werkzeug import check_password_hash, generate_password_hash
import rcdb
from collections import defaultdict
from rcdb.model import Run, Condition, ConditionType
from sqlalchemy.orm import subqueryload

from rcdb.provider import RCDBProvider
from runs.views import _parse_run_range

mod = Blueprint('select_values', __name__, url_prefix='/select_values')


@mod.route('/')
def index():
    all_conditions = g.tdb.session.query(ConditionType).order_by(ConditionType.name.asc()).all()

    return render_template("select_values/index.html",
                           all_conditions=all_conditions)
    pass


@mod.route('/search', methods=['GET'])
def search():
    all_conditions = g.tdb.session.query(ConditionType).order_by(ConditionType.name.asc()).all()
    run_range = request.args.get('rr', '')
    search_query = request.args.get('q', '')
    req_conditions_str = request.args.get('cnd', '')
    req_conditions_value = req_conditions_str.split(',')

    run_from_str = request.args.get('runFrom', '')
    run_to_str = request.args.get('runTo', '')

    if run_from_str or run_to_str:
        run_range = run_from_str + "-" + run_to_str

    args = {}
    run_from, run_to = _parse_run_range(run_range)

    try:
        table = g.tdb.select_values(val_names=req_conditions_value, search_str=search_query, run_min=run_from,
                                    run_max=run_to, sort_desc=True)
        print(req_conditions_value, run_from, run_to)
    except Exception as err:
        flash("Error in performing request: {}".format(err), 'danger')
        return redirect(url_for('select_values.index'))

    condition_types = g.tdb.get_condition_types()
    print(run_to, run_from)

    return render_template("select_values/index.html",
                           all_conditions=all_conditions,
                           run_range=run_range,
                           run_from=run_from,
                           run_to=run_to,
                           search_query=search_query,
                           req_conditions_value=req_conditions_value,
                           table=table)
