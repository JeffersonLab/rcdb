import json
import re
import sys
from time import mktime, time

import datetime

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, Response, jsonify
# from werkzeug import check_password_hash, generate_password_hash
import rcdb
from collections import defaultdict
from rcdb import DefaultConditions
from rcdb.model import Run, Condition, ConditionType, ConfigurationFile
from rcdb.stopwatch import StopWatchTimer
from rcdb_www.pagination import Pagination
from sqlalchemy import func
from sqlalchemy.orm import subqueryload, joinedload

mod = Blueprint('runs', __name__, url_prefix='/runs')

_nsre=re.compile("([0-9]+)")

def natural_sort_key(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)


PER_PAGE = 200


@mod.route('/', defaults={'page': 1, 'run_from': -1, 'run_to': -1})
@mod.route('/page/<int:page>', defaults={'run_from': -1, 'run_to': -1})
@mod.route('/<int:run_from>-<int:run_to>', defaults={'page': 1})
def index(page, run_from, run_to):

    start_time_stamp = int(time() * 1000)
    preparation_sw = StopWatchTimer()

    condition_types = g.tdb.get_condition_types()
    query = g.tdb.session.query(Run)

    # Run range is defined?
    if run_from != -1 and run_to != -1:

        # Check what is max/min run
        run_min, run_max = run_from, run_to
        if run_max < run_min:
            run_min, run_max = run_max, run_min

        # Filter query and count results
        query = query.filter(Run.number >= run_min, Run.number <= run_max)
        count = g.tdb.session.query(func.count(Run.number)).filter(Run.number >= run_min, Run.number <= run_max).scalar()

        # we don't want pagination in this case, setting page size same/bigger than count
        per_page = run_max - run_min
    else:
        count = g.tdb.session.query(func.count(Run.number)).scalar()
        per_page = PER_PAGE

    # Create pagination
    pagination = Pagination(page, per_page, count)

    preparation_sw.stop()
    query_sw = StopWatchTimer()
    # Get runs from query
    runs = query.options(subqueryload(Run.conditions))\
        .order_by(Run.number.desc())\
        .slice(pagination.item_limit_from, pagination.item_limit_to)\
        .all()
    query_sw.stop()
    performance = {
        "preparation": preparation_sw.elapsed,
        "query": query_sw.elapsed,
        "selection": 0.0,
        "start_time_stamp": start_time_stamp,
    }

    return render_template("runs/index.html", runs=runs,
                           DefaultConditions=DefaultConditions,
                           pagination=pagination,
                           condition_types=condition_types,
                           run_from=-1,
                           run_to=-1,
                           search_query="",
                           performance=performance)


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

    if rcdb.DefaultConditions.COMPONENT_STATS in conditions_by_name:
        component_stats = json.loads(conditions_by_name[rcdb.DefaultConditions.COMPONENT_STATS].value)
        component_sorted_keys = natural_sort_key([str(key) for key in component_stats.keys()])
    else:
        component_stats = None
        component_sorted_keys = None

    sorted_conditions = sorted(run.conditions, key=lambda x: x.name)

    important_files = []
    other_files = []
    for conf_file in run.files:
        if conf_file.importance == ConfigurationFile.IMPORTANCE_HIGH:
            important_files.append(conf_file)
        else:
            other_files.append(conf_file)

    return render_template("runs/info.html",
                           run=run,
                           conditions=sorted_conditions,
                           conditions_by_name=conditions_by_name,
                           component_stats=component_stats,
                           component_sorted_keys=component_sorted_keys,
                           DefaultConditions=rcdb.DefaultConditions,
                           prev_run=prev_run,
                           next_run=next_run,
                           important_files=important_files,
                           other_files=other_files
                           )


@mod.route('/elog/<int:run_number>')
def elog(run_number):

    try:
        from urllib2 import urlopen, HTTPError
    except ImportError:
        from urllib.request import urlopen
        from urllib.error import HTTPError
    try:
        elog_json = urlopen('https://logbooks.jlab.org/api/elog/entries?book=hdrun&title=Run_{}&limit=1'
                                    .format(run_number)).read()
    except HTTPError as e:
        return jsonify(stat=str(e.code))

    resp = Response(response=elog_json, status=200, mimetype="application/json")
    return resp


def _parse_run_range(run_range_str):
    """ Parses run range, returning a pair (run_from, run_to) or (run_from, None) or (None, None)

    Function doesn't raise FormatError
    :exception ValueError: if run_range_str is not str

    :param run_range_str: string to parse
    :return: (run_from, run_to). Function always return lower run number as run_from
    """

    if run_range_str is None:
        return None, None

    run_range_str = str(run_range_str).strip()
    if not run_range_str:
        return None, None

    assert isinstance(run_range_str, str)

    # Have run-range?
    if '-' in run_range_str:
        tokens = [t.strip() for t in run_range_str.split("-")]
        try:
            run_from = int(tokens[0])
        except (ValueError, KeyError):
            return None, None

        try:
            run_to = int(tokens[1])
        except (ValueError, KeyError):
            return run_from, None

        return (run_from, run_to) if run_from <= run_to else (run_to, run_from)

    # Have run number?
    if run_range_str.isdigit():
        return int(run_range_str), None

    # Default return is index
    return None, None


@mod.route('/search', methods=['GET'])
def search():
    run_range = request.args.get('rr', '')
    search_query = request.args.get('q', '')

    run_from_str = request.args.get('runFrom', '')
    run_to_str = request.args.get('runTo', '')
    if run_from_str or run_to_str:
        run_range = run_from_str + "-" + run_to_str


    args = {}
    run_from, run_to = _parse_run_range(run_range)

    if not search_query or not search_query.strip():
        if run_from is not None and run_to is not None:
            return redirect(url_for('.index', run_from=run_from, run_to=run_to))
        elif run_from is not None:
            return redirect(url_for('.info', run_number=run_from))
        else:
            return redirect(url_for('.index'))

    if run_from is None:
        run_from = 0

    if run_to is None:
        run_to = sys.maxint

    try:
        result = g.tdb.select_runs(search_query, run_to, run_from, sort_desc=True)
    except Exception as err:
        flash("Error in performing request: {}".format(err), 'danger')
        return redirect(url_for('.index'))
        # Create pagination
    pagination = Pagination(1, len(result.runs), len(result.runs))
    condition_types = g.tdb.get_condition_types()

    return render_template("runs/index.html",
                           runs=result.runs,
                           DefaultConditions=DefaultConditions,
                           pagination=pagination,
                           condition_types=condition_types,
                           run_from=run_from,
                           run_to=run_to if run_to != sys.maxint else -1,
                           search_query=search_query,
                           performance=result.performance)


@mod.route('/search2', methods=['GET'])
def search2():
    run_range = request.args.get('rr', '')
    search_query = request.args.get('q', '')
    columns = request.args.get('c', '')

    columns = columns.split(',')

    run_from_str = request.args.get('runFrom', '')
    run_to_str = request.args.get('runTo', '')
    if run_from_str or run_to_str:
        run_range = run_from_str + "-" + run_to_str

    args = {}
    run_from, run_to = _parse_run_range(run_range)

    if not search_query or not search_query.strip():
        if run_from is not None and run_to is not None:
            return redirect(url_for('.index', run_from=run_from, run_to=run_to))
        elif run_from is not None:
            return redirect(url_for('.info', run_number=run_from))
        else:
            return redirect(url_for('.index'))

    if run_from is None:
        run_from = 0

    if run_to is None:
        run_to = sys.maxint

    try:
        result = g.tdb.select_runs(search_query, run_to, run_from, sort_desc=True)
    except Exception as err:
        flash("Error in performing request: {}".format(err), 'danger')
        return redirect(url_for('.index'))
        # Create pagination
    pagination = Pagination(1, len(result.runs), len(result.runs))
    condition_types = g.tdb.get_condition_types()
    all_cnd_types_by_name = {cnd.name: cnd for cnd in condition_types}
    column_condition_types = [all_cnd_types_by_name[column] for column in columns]

    # Getting additional values and marking the run
    info_rows = result.get_values([DefaultConditions.IS_VALID_RUN_END]),
    for i, run in enumerate(result.runs):
        is_valid_run_end, = tuple(info_rows[i])
        run.is_valid_run_end = is_valid_run_end if is_valid_run_end is not None else False
        if i == 0 and run.end_time and not is_valid_run_end:
            run.is_active = True if (datetime.now() - run.end_time).total_seconds() < 120 else False
        else:
            run.is_active = False


    return render_template("runs/custom_column.html",
                           rows=result.get_values(columns, True),
                           column_condition_types=column_condition_types,
                           pagination=pagination,
                           condition_types=condition_types,
                           run_from=run_from,
                           run_to=run_to if run_to != sys.maxint else -1,
                           search_query=search_query,
                           performance=result.performance,
                           columns=columns)

















