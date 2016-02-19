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
#query = db.session.query(Run).join(Run.conditions).join(Condition.type)\
#        .filter(Run.number > 10000)\
#        .filter((ConditionType.name == "event_count"), (ConditionType.value_field < 950))\
#        .order_by(Run.number)

#db.create_condition_type("one", ConditionType.INT_FIELD, False)
#db.create_run(10171)
#db.add_condition(10171, "one", 10, None, True)
#db.add_condition(10171, "one", 11, None, True)
#run = db.get_run(10171)
#print [cnd for cnd in run.conditions if cnd.type.name == 'polarization_direction']

#eq = "(event_count)>5000 and polarization_direction == 'PARA'"

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


#query = db.session.query().add_entity(alias1).add_entity(alias2).filter((alias1._condition_type_id == ct1.id), (alias2._condition_type_id == ct2.id), (alias1.run_number == alias2.run_number)).options(joinedload(alias1.run)).order_by(alias1.run_number)
#print query
#print query.count()
#print query.all()



#        .filter(Run.number > 10000)\
#        .filter((ConditionType.name == "event_count"), (ConditionType.value_field < 950))\
#        .order_by(Run.number)

exit(1)

def get_comparison_value(db, entity):
    if isinstance(entity, ast.Num):
        return entity.n, None
    if isinstance(entity, ast.Name):
        name = entity.id
        ct = db.get_condition_type(name)
        assert isinstance(ct, ConditionType)
        return ct

eq = "event_count < 5 and "
runs = query.all()
for run in runs:
    cnd_by_name = run.get_conditions_by_name()
    print(eval("""cnd_by_name['event_count'].value if 'event_count' in cnd_by_name.keys() else 0"""))

print('')
print('')
print('')
print('')
try:
    tree = ast.parse(' 3.0 == event_count < 4.6 ')
    assert isinstance(tree, ast.AST)
    if len(tree.body) < 1:
        raise SyntaxError("Empty string")

    if not isinstance(tree.body[0], ast.Expr):
        raise SyntaxError("Is not an expression")

    expr = tree.body[0]
    isinstance(expr, ast.Expr)

    if isinstance(expr.value, ast.Compare):
        print expr.value.ops
        left = get_comparison_value(db, expr.value.left)
        right = get_comparison_value(db, expr.value.comparators[0])
        print "left =", left
        print "right =", right
        op = expr.value.ops[0]

        if isinstance(op, ast.Eq):
            query = query.filter(left == right)
        elif isinstance(op, ast.LtE):
            query = query.filter(left <= right)
        elif isinstance(op, ast.Lt):
            query = query.filter(left < right)
        elif isinstance(op, ast.GtE):
            query = query.filter(left >= right)
        elif isinstance(op, ast.Gt):
            query = query.filter(left > right)


    print ast.dump(tree)


except SyntaxError as ex:
    print("SyntaxError: {} before character {}".format(ex.message, ex.offset))

print()
print(shlex.split(" 3.0==  'event_count() horse' < 4.6"))


#Module(    body=[Expr(        value=Compare(left=Name(id='event_count', ctx=Load()), ops=[Gt()], comparators=[Num(n=5)]))])


