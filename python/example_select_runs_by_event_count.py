"""
test.py
python script to follow examples from RCDB wiki page


"""

from rcdb.provider import RCDBProvider


db = RCDBProvider("mysql://rcdb@hallddb/rcdb")

# get runs
runs = db.get_runs(10000, 20000)

for run in runs:
    conditions_by_name = run.get_conditions_by_name()

    event_count, = conditions_by_name['event_count']
    print(event_count)
