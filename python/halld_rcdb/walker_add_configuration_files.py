"""
Adds run_start_time and run_end_time conditions and fills them with run.start_time, run.end_time

"""
import argparse
import sys
import json

from rcdb import RCDBProvider

import run_config_parser
from rcdb.model import ConditionType, Run
from rcdb import DefaultConditions

import config_files_grabber

if __name__ == "__main__":
    print sys.argv
    # Get connection string from arguments
    parser = argparse.ArgumentParser(description="This example shows select runs and put them by dates")
    parser.add_argument("connection_string", nargs='?', default="mysql://rcdb@hallddb.jlab.org/rcdb")
    parser.add_argument("--run-start", default=0)
    parser.add_argument("--run-end", default=sys.maxint)

    args = parser.parse_args()

    # Open DB connection
    db = RCDBProvider(args.connection_string)

    print("Walking from run {}, to run {} ".format(args.run_start, args.run_end))

    # get all runs
    runs = db.get_runs(args.run_start, args.run_end)
    for run in runs:
        rtvs_value = run.get_condition_value("rtvs")
        if not rtvs_value:
            print("Skipping run {} not 'rtvs' condition".format(run.number))
            continue

        rtvs = json.loads(rtvs_value)
        config = rtvs['%(config)']

        run_config_file = db.get_file(run, config)
        if not run_config_file:
            print("Skipping run {} not 'main_config_file' is null or empty".format(run.number))
            continue

        parse_result = run_config_parser.parse_content(run_config_file.content)

        if not parse_result:
            continue

        config_files_grabber.grab_additional_configuration_files(parse_result)
        print ("Done run {}",format(run.number))
