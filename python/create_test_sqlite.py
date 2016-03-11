import os
from datetime import datetime

import rcdb
import sys
import argparse
from rcdb import ConditionType


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path of the sqlite database to create")
    args = parser.parse_args()
    print ("create database:")
    print args.path
    if os.path.exists(args.path):
        print "Such file already exists. Remove it first or give another path"
        exit(1)

    db = rcdb.RCDBProvider("sqlite:///"+args.path, check_version=False)
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
    print("database created")
