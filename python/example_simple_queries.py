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
    print sys.argv
    # Get connection string from arguments
    parser = argparse.ArgumentParser(description="This example shows basics of how to select runs using search queries")
    parser.add_argument("connection_string", help="RCDB connection string mysql://rcdb@localhost/rcdb")
    args = parser.parse_args()

    # Open DB connection
    db = RCDBProvider(args.connection_string)

    # Select production runs with event_count > 0.5M
    result = db.select_runs("@is_production and event_count > 500000", 10000, 20000)

    # Iterate through results
    for run in result:
        print run.number, run.get_condition_value("event_count")

    # Another way of getting values
    rows = result.get_values(["event_count", "polarization_direction", "beam_current"])