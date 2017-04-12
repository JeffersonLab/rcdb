"""

Usage:
    python get_values_fast.py <connectionstring>

"""

import argparse
import sys
from rcdb import RCDBProvider
from rcdb.model import run_periods
from sqlalchemy import text, bindparam, Integer

if __name__ == "__main__":
    # Get connection string from arguments
    parser = argparse.ArgumentParser(description="This example shows select runs and put them by dates")
    parser.add_argument("connection_string",
                        nargs='?',
                        help="RCDB connection string mysql://rcdb@localhost/rcdb",
                        default="mysql://rcdb@hallddb.jlab.org/rcdb")
    args = parser.parse_args()

    # Open DB connection
    db = RCDBProvider(args.connection_string)

    # Get runs from run period
    run_min, run_max, description = run_periods["2016-02"]
    print("Selecting runs {}-{} from run period: '{}'".format(run_min, run_max, description))

    # print resulting array
    # sql = text('SELECT * FROM runs WHERE number > :run')
    # sql.bindparams(run_number=30000)
    # result = db.session.connection().execute(sql, run=31000)
    # for row in result:
    # print row

    result = db.select_values(['event_count', 'daq_run', 'beam_energy', 'beam_current'], "@is_production", 30000)

    print (result.performance)

    for row in result:
        print (row)

