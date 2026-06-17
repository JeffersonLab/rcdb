#   E X A M P L E   5
# Make a pandas DataFrame for a set of runs (here the last 10):
#   rows    = the selected runs
#   columns = all known condition types
#   cells   = condition values (missing ones become NaN)

import pandas as pd

# import RCDB
from rcdb.provider import RCDBProvider
from rcdb.model import Run

# connect to DB
db = RCDBProvider("mysql://rcdb@hallddb.jlab.org/rcdb2")

# the last 10 runs (highest run numbers)
last_runs = [run.number for run in
             db.session.query(Run).order_by(Run.number.desc()).limit(10).all()]
print("Last {} runs: {}".format(len(last_runs), last_runs))

# all known condition names -> these become the DataFrame columns
condition_names = sorted(ct.name for ct in db.get_condition_types())

# select those values for exactly those runs (pass them via runs=)
table = db.select_values(condition_names, runs=last_runs)

# build the DataFrame: conditions as columns, run number as the index
df = pd.DataFrame(table.rows, columns=table.selected_conditions).set_index("run")

#   P R I N T   O U T
print(df)
print("It took {:.2f} sec ".format(table.performance['total']))
