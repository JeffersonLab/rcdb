import json
import re
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
# from werkzeug import check_password_hash, generate_password_hash
import rcdb
from collections import defaultdict
from rcdb import DefaultConditions
from rcdb.model import Run, BoardInstallation, Condition, ConditionType
from rcdb_www.pagination import Pagination
from run_table import RunTableData
from sqlalchemy import func
from sqlalchemy.orm import subqueryload, joinedload

mod = Blueprint('runs', __name__, url_prefix='/runs')

_nsre=re.compile("([0-9]+)")

def natural_sort_key(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)


PER_PAGE = 500


@mod.route('/', defaults={'page': 1})
@mod.route('/page/<int:page>')
def index(page):
    count = g.tdb.session.query(func.count(Run.number)).scalar()
    pagination = Pagination(page, PER_PAGE, count)

    runs = g.tdb.session.query(Run)\
        .options(subqueryload(Run.conditions))\
        .order_by(Run.number.desc())\
        .slice(pagination.item_limit_from, pagination.item_limit_to)\
        .all()

    return render_template("runs/index.html", runs=runs, DefaultConditions=DefaultConditions, pagination=pagination)
    pass


@mod.route('/conditions/<int:run_number>')
def conditions(run_number):
    run = g.tdb.session. \
        query(Run). \
        options(subqueryload(Run.conditions)). \
        filter_by(number=int(run_number)).one()

    return render_template("runs/conditions.html", run=run)


@mod.route('/info/<int:run_number>')
def info(run_number):
    """Shows run information and statistics
    :param run_number:
    """

    run = g.tdb.session \
        .query(Run) \
        .options(subqueryload(Run.conditions)) \
        .filter(Run.number == run_number) \
        .first()

    prev_run = g.tdb.get_prev_run(run_number)
    next_run = g.tdb.get_next_run(run_number)

    if not isinstance(run, Run):
        return render_template("runs/not_found.html", run_number=run_number, prev_run=prev_run, next_run=next_run)

    assert (isinstance(run, Run))
    conditions_by_name = run.get_conditions_by_name()

    # create board by crate list
    bi_by_crate = defaultdict(list)
    for bi in run.board_installations:
        bi_by_crate[bi.crate].append(bi)

    # sort boards by slot
    for bis in bi_by_crate.values():
        bis.sort(key=lambda x: x.slot)

    if rcdb.DefaultConditions.COMPONENT_STATS in conditions_by_name:
        component_stats = json.loads(conditions_by_name[rcdb.DefaultConditions.COMPONENT_STATS].value)
        component_sorted_keys = natural_sort_key([str(key) for key in component_stats.keys()])
    else:
        component_stats = None
        component_sorted_keys = None

    return render_template("runs/info.html",
                           run=run,
                           conditions=run.conditions,
                           conditions_by_name=conditions_by_name,
                           board_installs_by_crate=bi_by_crate,
                           component_stats=component_stats,
                           component_sorted_keys=component_sorted_keys,
                           DefaultConditions=rcdb.DefaultConditions,
                           prev_run=prev_run,
                           next_run=next_run
                           )


@mod.route('/search', methods=['GET'])
def search():
    search_query = request.args.get('q', '')

    if search_query:
        try:
            run_number = int(search_query)
            return redirect(url_for('.info', run_number=run_number))
        except ValueError:
            return redirect(url_for('.index'))
    else:
        return redirect(url_for('.index'))
