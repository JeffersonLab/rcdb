"""
Adds run_start_time and run_end_time conditions and fills them with run.start_time, run.end_time

"""
import argparse
import sys
from pprint import pprint
from rcdb.errors import OverrideConditionValueError
from rcdb import RCDBProvider
from rcdb.model import ConditionType, Run
from rcdb import DefaultConditions

if __name__ == "__main__":
    print("ARGS:")
    pprint(sys.argv)
    # Get connection string from arguments
    parser = argparse.ArgumentParser(description="This example shows select runs and put them by dates")
    parser.add_argument("connection_string", nargs='?', default="mysql://rcdb@hallddb.jlab.org/rcdb")
    args = parser.parse_args()

    # Open DB connection
    db = RCDBProvider(args.connection_string)

    # add two conditions type. If they are already exist this function just does nothing
    db.create_condition_type(DefaultConditions.RUN_START_TIME, ConditionType.TIME_FIELD, "Run start time by DAQ")
    db.create_condition_type(DefaultConditions.RUN_END_TIME, ConditionType.TIME_FIELD, "Run end time by DAQ")

    # get all runs
    runs = db.get_runs(0, sys.maxsize)
    for run in runs:
        print(run.number)
        try:
            start_time_cnd_value = db.get_condition(run, DefaultConditions.RUN_START_TIME)
            end_time_cnd_value = db.get_condition(run, DefaultConditions.RUN_END_TIME)
            if run.start_time and not start_time_cnd_value:
                print(f"Adding start time {run.start_time}")
                db.add_condition(run, DefaultConditions.RUN_START_TIME, run.start_time)                
            if run.end_time and not end_time_cnd_value:
                print(f"Adding end time {run.end_time}")
                db.add_condition(run, DefaultConditions.RUN_END_TIME, run.end_time)
        except OverrideConditionValueError as ex:
            print(ex)

