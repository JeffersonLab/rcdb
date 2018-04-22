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
    runs = {}
    # create runs
    for i in range(1, 6):
        runs[i] = db.create_run(i)

    runs[9] = db.create_run(9)

    db.create_condition_type("a", ConditionType.INT_FIELD, "Test condition 'a'")
    db.create_condition_type("b", ConditionType.FLOAT_FIELD, "Test condition 'b'")
    db.create_condition_type("c", ConditionType.BOOL_FIELD, "Test condition 'v'")
    db.create_condition_type("d", ConditionType.STRING_FIELD, "Test condition 'd'")
    db.create_condition_type("e", ConditionType.JSON_FIELD, "Test condition 'e'")
    db.create_condition_type("f", ConditionType.STRING_FIELD, "Test condition 'f'")
    db.create_condition_type("g", ConditionType.BLOB_FIELD, "Test condition 'g'")

    # create conditions
    db.add_condition(1, "a", 1)
    db.add_condition(2, "a", 2)
    db.add_condition(3, "a", 3)
    db.add_condition(4, "a", 4)
    db.add_condition(9, "a", 9)

    db.add_condition(1, "b", 1.01)
    db.add_condition(2, "b", 7.0 / 3.0)
    db.add_condition(3, "b", 2.55)
    db.add_condition(4, "b", 1.64)
    db.add_condition(5, "b", 2.32)
    db.add_condition(9, "b", 2.02)

    db.add_condition(1, "c", False)
    db.add_condition(2, "c", True)
    db.add_condition(3, "c", True)
    db.add_condition(4, "c", True)
    db.add_condition(5, "c", False)
    db.add_condition(9, "c", True)

    db.add_condition(1, "d", "haha")
    db.add_condition(4, "d", "hoho")
    db.add_condition(5, "d", "bang")
    db.add_condition(9, "d", "mew")

    db.add_condition(1, "e", '{"a":1}')
    db.add_condition(4, "e", "[1,2,3]")
    db.add_condition(9, "e", '[3,2,{"b":5}]')

    db.add_condition(4, "f", "my only value")

    db.add_condition(5, "g", "aGVsbG8gd29ybGQ=")

    """
    run |     a     |     b     |     c     |      d     |     e         |     f         |     g  
    -----------------------------------------------------------------------------------------------------   
      1 | 1         | 1.01      | False     | haha       | {"a":1}       | None          | None   
      2 | 2         | 2.333...  | True      | None       | None          | None          | None   
      3 | 3         | 2.55      | True      | None       | None          | None          | None   
      4 | 4         | 1.64      | True      | hoho       | [1,2,3]       | my only value | None 
      5 | None      | 2.32      | False     | bang       | None          | None          | aGVsbG8gd29ybGQ=   
      9 | 9         | 2.02      | True      | mew        | [3,2,{"b":5}] | None          | None   

    """


if __name__ == "__main__":

    # Tell the dangers!

    print("This script is to create DB schema and fill it with test values to run UNIT TESTS")
    print("(!) WARNING the database structure will be removed and recreated. All data will be lost")

    parser = argparse.ArgumentParser()
    parser.add_argument("connection_str", help="Connection string to the database")
    args = parser.parse_args()

    connection_str = args.connection_str

    # validate SQLite link
    if connection_str.startswith("sqlite") and os.path.exists(connection_str[10:]):
        print ("Such file already exists. Remove it first or give another path")
        exit(1)

    # Connection to DB
    db = rcdb.RCDBProvider(connection_str, check_version=False)

    # Create DB structure
    create_db_structure(db)

    print("database created")
