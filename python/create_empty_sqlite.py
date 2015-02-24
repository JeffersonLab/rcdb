import os
import rcdb
import sys
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path of the sqlite database to create")
    args = parser.parse_args()
    print ("create database:")
    print args.path
    if os.path.exists(args.path):
        print "Such file already exists. Remove it first or give another path"
        exit(1)

    db = rcdb.ConfigurationProvider("sqlite:///"+args.path)
    rcdb.model.Base.metadata.create_all(db.engine)
    # create run
    db.create_run(0)
    db.create_run(1)
    print("database created")
