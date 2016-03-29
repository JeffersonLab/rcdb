import os
from datetime import datetime

import rcdb
import argparse
from rcdb import ConditionType


def create_db_structure(db):
    """Creates schema and fill it with values

    :param db: rcdb.RCDBProvider for the database
    :type db: rcdb.RCDBProvider
    """
    assert isinstance(db, rcdb.RCDBProvider)

    rcdb.provider.destroy_all_create_schema(db)

    # create run
    db.create_run(1)
    db.create_run(2)
    db.create_condition_type("bool_cnd", ConditionType.BOOL_FIELD, "bool condition")
    db.create_condition_type("json_cnd", ConditionType.JSON_FIELD, "JSon condition")
    db.create_condition_type("string_cnd", ConditionType.STRING_FIELD, "string condition")
    db.create_condition_type("float_cnd", ConditionType.FLOAT_FIELD, "float condition")
    db.create_condition_type("int_cnd", ConditionType.INT_FIELD, "Int condition")
    db.create_condition_type("time_cnd", ConditionType.TIME_FIELD, "Time condition")
    db.create_condition_type("blob_cnd", ConditionType.BLOB_FIELD, "BLOB condition")

    db.add_condition(1, "bool_cnd", True)
    db.add_condition(2, "bool_cnd", False)

    db.add_condition(1, "json_cnd", '{"firstName":"John", "lastName":"Doe"}')
    db.add_condition(2, "json_cnd", '{"firstName":"Elton", "lastName":"Smith"}')

    db.add_condition(1, "string_cnd", "hey")
    db.add_condition(2, "string_cnd", "ho")

    db.add_condition(1, "float_cnd", 0.1)
    db.add_condition(2, "float_cnd", 2.2)

    db.add_condition(1, "int_cnd", 5)
    db.add_condition(2, "int_cnd", 10)

    db.add_condition(1, "time_cnd", datetime(2009, 1, 6, 15, 8, 24, 78915))
    db.add_condition(2, "time_cnd", datetime(2010, 1, 2, 3, 4, 5, 6))

    db.add_condition(1, "blob_cnd", "F4D1")
    db.add_condition(2, "blob_cnd", "1235")

    # Run with not all conditions filled
    db.create_run(3)
    db.add_condition(3, "float_cnd", -0.2)
    db.add_condition(3, "int_cnd", 20)


if __name__ == "__main__":

    # Tell the dangers!

    print "This script is to create DB schema and fill it with test values to run UNIT TESTS"
    print "(!) WARNING the database structure will be removed and recreated. All data will be lost"

    parser = argparse.ArgumentParser()
    parser.add_argument("connection_str", help="Connection string to the database")
    args = parser.parse_args()

    connection_str = args.connection_str

    # validate SQLite link
    if connection_str.startswith("sqlite") and os.path.exists(connection_str[10:]):
        print "Such file already exists. Remove it first or give another path"
        exit(1)

    # Connection to DB
    db = rcdb.RCDBProvider(connection_str, check_version=False)

    # Create DB structure
    create_db_structure(db)

    print("database created")
