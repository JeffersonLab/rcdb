import os
from datetime import datetime

import rcdb
import argparse
from rcdb import ConditionType


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path of the sqlite database to create")
    args = parser.parse_args()

    print("create database:")
    print args.path
    if os.path.exists(args.path):
        print "Such file already exists. Remove it first or give another path"
        #exit(1)

    con_str = "sqlite:///"+args.path
    db = rcdb.RCDBProvider(con_str, check_version=False)
    rcdb.provider.destroy_all_create_schema(db)
    # create run
    print("database created")
