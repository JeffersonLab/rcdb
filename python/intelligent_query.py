import ast
from token import NAME

from ply.lex import LexToken

import rcdb
import rcdb.lexer
from rcdb.model import ConditionType, Run, Condition
from sqlalchemy import or_, and_
from sqlalchemy.orm import joinedload, aliased
import shlex
import ast

db = rcdb.RCDBProvider("mysql://rcdb@127.0.0.1/rcdb")
#query = db.session.query(Run).join(Run.conditions).join(Condition.type)\
#        .filter(Run.number > 10000)\
#        .filter((ConditionType.name == "event_count"), (ConditionType.value_field < 950))\
#        .order_by(Run.number)

db.create_condition_type("one", ConditionType.INT_FIELD, False)
db.create_run(10171)
db.add_condition(10171, "one", 10, None, True)
db.add_condition(10171, "one", 11, None, True)
run = db.get_run(10171)
print [cnd for cnd in run.conditions if cnd.type.name == 'polarization_direction']

eq = "(event_count)>5000 and polarization_direction == 'PARA'"

cnd_types = {cnd.name: cnd for cnd in db.get_condition_types()}
all_cnd_names = [str(key) for key in cnd_types.keys()]


print all_cnd_names
tokens = [token for token in rcdb.lexer.tokenize(eq)]
print tokens

target_cnd_types=[]
alchemy_comparisons=[]
names = []
queries = []
for token in tokens:
    if token.type != "NAME":
        continue

    if token.value not in all_cnd_names:
        print("name '{}' is not found in ConditionTypes".format(token.value))
        exit(1)
    else:
        target_cnd_types.append(cnd_types[token.value])
        cnd_name = token.value
        token.value = "cnd_by_name['{}'].value".format(cnd_name)
        alchemy_comparisons.append((ConditionType.name == cnd_name))
        names.append(cnd_name)
        queries.append(db.session.query(Run).join(Run.conditions).join(Condition.type).filter(Run.number > 1).filter((ConditionType.name != cnd_name)))


print alchemy_comparisons

search_eval = " ".join([token.value for token in tokens if isinstance(token, LexToken)])

print search_eval

alias1 = aliased(ConditionType)
cnd_al1 = aliased(Condition)
alias2 = aliased(ConditionType)
cnd_al2 = aliased(Condition)

query = db.session.query(Run).join(cnd_al1, Run.conditions).join(cnd_al2, Run.conditions).join(alias1, cnd_al1.type).join(alias2, cnd_al2.type)\
    .filter(alias1.name == 'event_count', alias2.name == 'polarization_direction')

runs = query.all()
print query
#print runs
compiled_search_eval = compile(search_eval,'<string>','eval')
print "Begin search"

sel_runs=[]
for run in runs:

    cnd_by_name = run.get_conditions_by_name()
    if(eval(compiled_search_eval)):
        sel_runs.append(run.number)
print sel_runs
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


