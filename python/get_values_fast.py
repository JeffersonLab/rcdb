"""
Experiments with getting values faster
Usage:
   python example_simple_queries.py <connectionstring>

"""
import argparse
import sys
from rcdb import RCDBProvider, ConditionType
from rcdb.model import Condition
from rcdb.stopwatch import StopWatchTimer
from sqlalchemy import desc
from sqlalchemy.orm import aliased

if __name__ == "__main__":
    print sys.argv
    # Get connection string from arguments
    parser = argparse.ArgumentParser(description="This example shows basics of how to select runs using search queries")
    parser.add_argument("connection_string", help="RCDB connection string mysql://rcdb@localhost/rcdb")
    parser.add_argument('target_cnd_names', nargs='*')
    args = parser.parse_args()

    print "Conditions:", args.target_cnd_names

    # Open DB connection
    db = RCDBProvider(args.connection_string)

    sw = StopWatchTimer()
    sw.start()

    # Select production runs with event_count > 0.5M
    result = db.select_runs("event_count > 100", 0, 20000)



    #result.runs = db.get_runs(0, 20000)

    sw.stop()
    print "Selection took ", sw.elapsed

    print("Selected {} runs".format(len(result.runs)))

    print result.get_values(args.target_cnd_names, insert_run_number=True)

    exit(0)

    all_cnt_types = db.get_condition_types()
    all_cnd_types_by_name = {cnd.name: cnd for cnd in all_cnt_types}
    all_cnd_names = [str(key) for key in all_cnd_types_by_name.keys()]

    target_cnd_types = []
    for cnd_name in args.target_cnd_names:
        target_cnd_types.append(all_cnd_types_by_name[cnd_name])

    target_cnd_types = sorted(target_cnd_types, key=lambda x: x.id)
    target_cnd_types_len = len(target_cnd_types)


    print target_cnd_types

    ids = [ct.id for ct in target_cnd_types]
    run_numbers = [r.number for r in result.runs]
    sw = StopWatchTimer()
    sw.start()
    query = db.session.query(Condition)\
        .filter(Condition._condition_type_id.in_(ids), Condition.run_number.in_(run_numbers))\
        .order_by(Condition.run_number, Condition._condition_type_id)

    conditions = query.all()
    sw.stop()
    print "Getting conditions took ", sw.elapsed
    print ("Selected {} conditions".format(len(conditions)))

    sw = StopWatchTimer()
    sw.start()
    select_count = 0

    rows = []
    row = [None] * target_cnd_types_len
    type_index = 0
    prev_run = conditions[0].run_number
    conditions_iter = 0
    conditions_len = len(conditions)

    for condition in conditions:
        assert isinstance(condition, Condition)
        conditions_iter += 1

        type_id = condition._condition_type_id
        if condition.run_number != prev_run or conditions_len == conditions_iter:
            rows.append(row)
            row = list([None] * target_cnd_types_len)
            prev_run = condition.run_number
            if conditions_len != conditions_iter:
                type_index = 0

        while type_index < target_cnd_types_len and type_id != target_cnd_types[type_index].id:
            type_index += 1
            if type_index == target_cnd_types_len:
                type_index = 0
        row[type_index] = condition

    sw.stop()
    print "Iterating took ", sw.elapsed



