from flask import Blueprint, request, render_template, flash, g, redirect, url_for
from rcdb.model import ConditionType, RunPeriod, RCDB_MAX_RUN
from runs.views import _parse_run_range

mod = Blueprint('select_values', __name__, url_prefix='/select_values')


@mod.route('/', methods=['GET'])
def index():
    # noinspection PyUnresolvedReferences
    all_conditions = g.tdb.session.query(ConditionType).order_by(ConditionType.name.asc()).all()
    run_periods = g.tdb.session.query(RunPeriod).all()

    run_from_str = request.args.get('runFrom', '')
    run_to_str = request.args.get('runTo', '')
    req_conditions_str = request.args.get('cnd', '')

    # Check if there are search parameters in the URL
    if 'q' in request.args:
        # Handle search request
        search_query = request.args.get('q', '')
        run_range = request.args.get('rr', '')
        req_conditions_values = req_conditions_str.split(',')

        if run_from_str or run_to_str:
            run_range = run_from_str + "-" + run_to_str

        run_from, run_to = _parse_run_range(run_range)

        # If run_to is none, this means that it is infinite
        if run_to is None:
            run_to = RCDB_MAX_RUN

        try:
            table = g.tdb.select_values(val_names=req_conditions_values,
                                        search_str=search_query,
                                        run_min=run_from,
                                        run_max=run_to,
                                        sort_desc=True)
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

