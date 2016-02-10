"""
test.py
python script to follow examples from RCDB wiki page


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
    event_count = run.get_condition('event_count').value
    print(event_count)
