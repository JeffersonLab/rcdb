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
runs = db.select_runs("@is_production", 0, 20000)
sw.stop()
print sw.elapsed, len(runs)

sw = StopWatchTimer()
sw.start()
runs = db.select_runs("@is_cosmic", 0, 20000)
sw.stop()
print sw.elapsed, len(runs)

sw = StopWatchTimer()
sw.start()
runs = db.select_runs("@is_production", 0, 20000)
sw.stop()
print sw.elapsed, len(runs)

