import ast
from timeit import default_timer
from token import NAME

from ply.lex import LexToken

import rcdb
import rcdb.lexer
from rcdb import RCDBProvider
from rcdb.model import ConditionType, Run, Condition
from sqlalchemy import or_, and_
from sqlalchemy.orm import joinedload, aliased
import shlex
import ast

from rcdb.stopwatch import StopWatchTimer

db = rcdb.RCDBProvider("mysql://rcdb@127.0.0.1/rcdb")

"""
.session \
.query(Run) \
.options(subqueryload(Run.conditions)) \
.filter(Run.number == run_number) \
.first()
"""

sw = StopWatchTimer()
sw.start()
runs = db.select_runs("event_count>10000 and 'TRG' in run_config", 0, 20000)
sw.stop()
print sw.elapsed, len(runs)

sw = StopWatchTimer()
sw.start()
runs = db.select_runs("event_count!=0 and run_config.startswith('TRG')")
sw.stop()
print sw.elapsed

sw = StopWatchTimer()
sw.start()
runs = db.select_runs("event_count!=0 and daq_run")
sw.stop()
print sw.elapsed

sw = StopWatchTimer()
sw.start()
runs = db.select_runs("event_count!=0 and daq_run")
sw.stop()
print sw.elapsed, runs

sw = StopWatchTimer()
sw.start()
runs = db.select_runs("event_count!=0 and daq_run")
sw.stop()
print sw.elapsed

sw = StopWatchTimer()
sw.start()
runs = db.select_runs("event_count!=0 and daq_run")
sw.stop()
print sw.elapsed

for run in runs:
    print run.number, run.conditions


text = runs.to_csv(["run_number", "event_count", "magnet_current"])
table = runs.to_table   # ...


ct1 = db.get_condition_type('event_count')
ct2 = db.get_condition_type('daq_run')

alias1 = aliased(Condition)
alias2 = aliased(Condition)

