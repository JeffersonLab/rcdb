"""
Adds run_start_time and run_end_time conditions and fills them with run.start_time, run.end_time

"""
import argparse
import json
import os
import sys

from rcdb import ConfigurationProvider
from rcdb.model import ConfigurationFile, RCDB_MAX_RUN
from . import roc_config_finder
from . import run_config_parser

if __name__ == "__main__":
    print(sys.argv)
    # Get connection string from arguments
    parser = argparse.ArgumentParser(description="This example shows select runs and put them by dates")
    parser.add_argument("connection_string", nargs='?', default="mysql://rcdb@hallddb.jlab.org/rcdb")
    parser.add_argument("--run-start", default=0)
    parser.add_argument("--run-end", default=RCDB_MAX_RUN)
    parser.add_argument('--save', action='store_true')

    args = parser.parse_args()

    # Open DB connection
    db = ConfigurationProvider(args.connection_string)

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

        grab_infos = roc_config_finder.find_roc_configuration_files(parse_result)
        for info in grab_infos:
            info.print_self()
            print("{}:".format(info.name))
            for file_path in info.final_files:
                if os.path.isfile(file_path) and os.access(file_path, os.R_OK):
                    print("   {}".format(file_path))
                    if args.save:
                        db.add_configuration_file(run.number,
                                                  file_path,
                                                  importance=ConfigurationFile.IMPORTANCE_LOW)

        print("Done run {}\n".format(run.number))
