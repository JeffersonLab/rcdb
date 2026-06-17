#   E X A M P L E   6
# Make a pandas DataFrame of the configuration/log files saved for runs:
#   rows    = the last 10 runs
#   columns = every file path seen across those runs
#   cells   = the file's sha256 hash for that run, or NaN if the run has no such file

import pandas as pd

# import RCDB
from rcdb.provider import RCDBProvider
from rcdb.model import Run

# connect to DB
db = RCDBProvider("mysql://rcdb@hallddb.jlab.org/rcdb2")

# the last 10 runs (highest run numbers)
runs = db.session.query(Run).order_by(Run.number.desc()).limit(10).all()

# for each run map every saved file path -> its hash
# (run.files is the list of ConfigurationFile objects attached to the run)
file_hashes = {run.number: {f.path: f.sha256 for f in run.files} for run in runs}

# build the DataFrame: file paths as columns, run number as the index.
# from_dict fills missing files with NaN, so a cell is the hash if the file
# exists for that run and NaN otherwise.
df = pd.DataFrame.from_dict(file_hashes, orient="index").sort_index()
df.index.name = "run"

#   P R I N T   O U T
print("{} runs x {} distinct files".format(df.shape[0], df.shape[1]))
print(df)
