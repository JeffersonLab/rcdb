import sys

from flask import Blueprint, request, render_template, flash, g, redirect, url_for
from sqlalchemy import desc

from rcdb.model import ConditionType, RunPeriod
from rcdb.web.modules.runs import _parse_run_range

mod = Blueprint('select_values', __name__, url_prefix='/select_values')


@mod.route('/', methods=['GET'])
def index():
    # noinspection PyUnresolvedReferences
    all_conditions = g.tdb.session.query(ConditionType).order_by(ConditionType.name.asc()).all()
    run_periods = g.tdb.session.query(RunPeriod).order_by(desc(RunPeriod.start_date)).all()

    run_from_str = request.args.get('runFrom', '')
    run_to_str = request.args.get('runTo', '')
    req_conditions_str = request.args.get('cnd', '')

    # Check if there are search parameters in the URL
    if 'q' in request.args:
        # Handle search request
        search_query = request.args.get('q', '')
        run_range = request.args.get('rr', '')
        # Drop blanks so an empty field or trailing comma doesn't become a bogus condition name
        req_conditions_values = [name.strip() for name in req_conditions_str.split(',') if name.strip()]

        if run_from_str or run_to_str:
            run_range = run_from_str + "-" + run_to_str

        run_from, run_to = _parse_run_range(run_range)

        # An empty field means "no bound" - map it to the full run range the API expects
        run_min = run_from if run_from is not None else 0
        run_max = run_to if run_to is not None else sys.maxsize

        try:
            table = g.tdb.select_values(val_names=req_conditions_values, search_str=search_query, run_min=run_min,
                                        run_max=run_max, sort_desc=True)
        except Exception as err:
            flash("Error in performing request: {}".format(err), 'danger')
            return redirect(url_for('select_values.index'))

        return render_template("select_values/index.html",
                               all_conditions=all_conditions,
                               run_periods=run_periods,
                               run_range=run_range,
                               run_from=run_from,
                               run_to=run_to,
                               search_query=search_query,
                               req_conditions_str=req_conditions_str,
                               req_conditions_values=req_conditions_values,
                               table=table)

    # Handle regular index page request
    return render_template("select_values/index.html",
                           all_conditions=all_conditions,
                           run_periods=run_periods,
                           run_from_str=run_from_str,
                           run_to_str=run_to_str,
                           req_conditions_str=req_conditions_str)

