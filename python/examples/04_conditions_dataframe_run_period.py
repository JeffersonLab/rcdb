#   E X A M P L E   4
# Make a pandas DataFrame for a whole run period:
#   rows    = runs of the period
#   columns = all known condition types
#   cells   = condition values (missing ones become NaN)

import pandas as pd

# import RCDB
from rcdb.provider import RCDBProvider

# connect to DB
db = RCDBProvider("mysql://rcdb@hallddb.jlab.org/rcdb2")

# pick a run period (here the latest one by run number)
run_period = max(db.get_run_periods(), key=lambda rp: rp.run_max)
print("Run period: {} [{}-{}]".format(run_period.name, run_period.run_min, run_period.run_max))

# all known condition names -> these become the DataFrame columns
condition_names = sorted(ct.name for ct in db.get_condition_types())

# select those values for every run in the period
table = db.select_values(condition_names, run_min=run_period.run_min, run_max=run_period.run_max)

# build the DataFrame: conditions as columns, run number as the index
df = pd.DataFrame(table.rows, columns=table.selected_conditions).set_index("run")

#   P R I N T   O U T
print(df)
print("It took {:.2f} sec ".format(table.performance['total']))
