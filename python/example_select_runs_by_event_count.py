"""
Select event_count condition for selected runs
"""

from rcdb.provider import RCDBProvider


db = RCDBProvider("mysql://rcdb@hallddb/rcdb")

# get runs
runs = db.get_runs(10000, 20000)

# All conditions of this run by name.
conditions_by_name = runs[0].get_conditions_by_name()
print(conditions_by_name.keys())

for run in runs:
    # Remember that get_condition() function returns Condition object. Call .value to get the value
    event_count_cnd = run.get_condition('event_count')

    # get_condition returns None if no such condition is written for tun
    if event_count_cnd:
        print(event_count_cnd.value)
    else:
        print("no event_count for run", run.number)

