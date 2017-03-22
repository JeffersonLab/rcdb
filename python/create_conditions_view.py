import os
import rcdb
import argparse

from rcdb import ConditionType

description = """
Test script that create conditions_view for all existing conditions

"""
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-c", "--connection", default=os.environ.get('RCDB_CONNECTION', None), help="Connection string for mysql database")
    args = parser.parse_args()
    if not args.connection:
        print("Set RCDB connection to run the script")
        exit(1)

    print ("creating database:")
    db = rcdb.RCDBProvider(args.connection, check_version=False)
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