"""
This example shows basics of how to select runs using search queries

This example requires some live databse

Usage:
   python example_simple_queries.py <connectionstring>

"""
import argparse
import sys
from rcdb import RCDBProvider


if __name__ == "__main__":
    print(sys.argv)
    # Get connection string from arguments
    parser = argparse.ArgumentParser(description="This example shows basics of how to select runs using search queries")
    parser.add_argument("connection_string", help="RCDB connection string mysql://rcdb@localhost/rcdb",
                        nargs='?', default='mysql://rcdb@hallddb.jlab.org/rcdb')
    args = parser.parse_args()

    # Open DB connection
    db = RCDBProvider(args.connection_string)

    # Select production runs with event_count > 0.5M
    result = db.select_values(["event_count", "polarization_direction", "beam_current"],
                              "@is_production and event_count > 500000", 10000, 20000)

    # print title
    print("{:>7} {:>15} {:>15} {:>15}".format('run', 'polarization_direction', 'beam_current', 'event_count'))

    # Iterate through results
    for row in result:
        run, event_count, polarization_direction, beam_current = tuple(row)
        print("{:>7} {:>15} {:>15} {:>15}".format(run, polarization_direction, beam_current, event_count))

