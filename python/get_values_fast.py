"""
Experiments with getting values faster
Usage:
   python example_simple_queries.py <connectionstring>

"""
import argparse
import sys
from rcdb import RCDBProvider, ConditionType
from rcdb.model import Condition
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

    # Select production runs with event_count > 0.5M
    runs = db.select_runs("@is_production and event_count > 500000", 10000, 20000)



    all_cnt_types = db.get_condition_types()
    all_cnd_types_by_name = {cnd.name: cnd for cnd in all_cnt_types}
    all_cnd_names = [str(key) for key in all_cnd_types_by_name.keys()]

    target_cnd_types = []
    names = []
    aliased_cnd_types = []
    aliased_cnd = []
    queries = []
    names_count = 0
    for cnd_name in args.target_cnd_names:
        cnd_type = all_cnd_types_by_name[cnd_name]
        target_cnd_types.append(cnd_type)
        names_count += 1
        names.append(cnd_name)
        aliased_cnd.append(aliased(Condition))
        aliased_cnd_types.append(aliased(ConditionType))
        queries.append(db.session.query(cnd_type.get_condition_alias_value_field(Condition)).filter(Condition._condition_type_id == cnd_type.id,  Condition.run_number > 10500).order_by(Condition.run_number))



    #for (i, query) in enumerate(queries):
    #    if i == 0:
    #        continue

    queries[0] = queries[0].union(queries[1], queries[2])

    # query = db.session.query(target_cnd_types[0].get_condition_alias_value_field(Condition)).filter(Condition._condition_type_id == target_cnd_types[0].id,  Condition.run_number > 10500)

    #
    # for (i, alias_cnd) in enumerate(aliased_cnd):
    #     alias_cnd_type = aliased_cnd_types[i]
    #     cnd_type = target_cnd_types[i]
    #
    #     query = query.add_entity(alias_cnd)\
    #         .filter(alias_cnd._condition_type_id == cnd_type.id)
    #     if i != 0:
    #         query = query.filter(alias_cnd.run_number == aliased_cnd[0].run_number)
    #
    # # apply sorting
    # sort_desc = False
    # if not sort_desc:
    #     query = query.order_by(aliased_cnd[0].run_number)
    # else:
    #     query = query.order_by(desc(aliased_cnd[0].run_number))

    #query = query.filter(aliased_cnd[0].run_number >= run_min, aliased_cnd[0].run_number <= run_max) \.join(aliased_cnd[0].run)


    values = queries[0].all()

    for value in values:
        print value