import os
import rcdb
import argparse

from rcdb import ConditionType

description = """
Test script that create conditions_view for all existing conditions

"""
if __name__ == "__main__":
    # Get connection string from arguments
    parser = argparse.ArgumentParser(description="This example shows select runs and put them by dates")
    parser.add_argument("connection_string",
                        nargs='?',
                        help="RCDB connection string mysql://rcdb@localhost/rcdb",
                        default="mysql://rcdb@hallddb.jlab.org/rcdb")
    args = parser.parse_args()

    # Open DB connection
    db = rcdb.RCDBProvider(args.connection_string)

    condition_types = db.get_condition_types()

    query = "SELECT runs.number run" + os.linesep
    query_joins = " FROM runs " + os.linesep
    for ct in condition_types:
        assert isinstance(ct, ConditionType)
        table_name = ct.name + "_table"
        query += "  ,{}.{} {}{}".format(table_name, ct.get_value_field_name(), ct.name, os.linesep)
        query_joins += "  LEFT JOIN conditions {0} " \
                       "  ON {0}.run_number = runs.number AND {0}.condition_type_id = {1}{2}"\
            .format(table_name, ct.id, os.linesep)

        print(ct)

    print("QUERY:")
    print(query + query_joins)