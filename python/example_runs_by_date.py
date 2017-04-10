"""
Example shows how to select runs and some data (event_count) and show it by date

The script result is something like: 

Selecting runs 10000-19999 from run period: '28 Jan 2016 - 24 Apr 2016   Commissioning, 12 GeV e-'
'2016-02-20' has 6 runs 10391 - 10399
		10391	2016-02-20 07:29:04   84235408
		10392	2016-02-20 10:33:11   51150478		
		...
'2016-02-21' has 10 runs 10412 - 10436
		10412	2016-02-21 02:42:24   59020003
		10414	2016-02-21 05:00:05   21921629
		...
...

Usage:
    python example_runs_by_date.py <connectionstring>

"""
import argparse
import sys
from rcdb import RCDBProvider
from rcdb.model import run_periods


def get_runs_by_date(db, query, run_min=0, run_max=sys.maxint):
    """
    Returns dictionary of dates with all runs per date
    
    :param db: RCDB provider class (aka rcdb.RCDBProvider)
    :param query: Run search query. All runs are selected if blank
    :param run_min: Run to start search from
    :param run_max: Run (included) to search up to  
    :return: (data_by_date, performance) where data_by_date in form {date: [(run_number, start_time, event_count),...]}
    
    :description:
    
    """

    assert isinstance(db, RCDBProvider)

    # Select production runs with event_count > 0.5M
    result = db.select_runs(query, run_min, run_max)
    event_counts = result.get_values("event_count", insert_run_number=False)

    # at this point event_counts is a table of one column and many rows
    # like [[84235408L], [51150478L], [35548286L], ...]
    # we want it to be just a vector with values [84235408L, 51150478L, 35548286L, ...]
    event_counts = [ec[0] for ec in event_counts]

    # Here we can see exact performance budget. All in seconds
    # >oO DEBUG print("Performance: ", result.performance)

    # construct data by date
    data_by_date = {}
    for run, event_count in zip(result, event_counts):
        run_date = run.start_time.date()

        # is there the key already?
        if run_date not in data_by_date:
            data_by_date[run_date] = []

        # add data to corresponding date
        data_by_date[run_date].append((run.number, run.start_time, event_count))
    return data_by_date, result.performance


if __name__ == "__main__":
    print sys.argv
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

    data_by_date, performance = get_runs_by_date(db, "@status_approved and @is_production", run_min, run_max)

    # print performance. All is in seconds
    print("Performance([sec]) is: ", performance)

    # print resulting array
    for run_date in sorted(data_by_date.keys()):
        run_values = data_by_date[run_date]
        print("'{}' has {} runs {} - {}".format(
            run_date,
            len(run_values),
            run_values[0][0],       # run_values[x] is (run_num, start_time, events) => run_values[x][0] is run_num
            run_values[-1][0]
        ))

        for run_num, start_time, events in run_values:
            print("\t\t{}\t{}   {}".format(run_num, start_time, events))
