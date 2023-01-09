"""
The script re-parses old sqlite database of the Fall 2014 format and fills conditions according to the run
"""
import argparse
import sqlite3
import sys
from flask import logging
import rcdb.model
from rcdb import ConfigurationProvider
from rcdb import coda_parser
from rcdb.file_archiver import get_file_sha256, get_string_sha256

import xml.etree.ElementTree as ET

# setup logger
log = logging.getLogger('rcdb')                     # create run configuration standard logger
log.addHandler(logging.StreamHandler(sys.stdout))   # add console output for logger
log.setLevel(logging.DEBUG)

if __name__ == "__main__":

    # hello
    print ("This program takes sqlite file of RCDB with data taken prior 2015" \
           " and add to a database with new format")

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("in_sqlite_file", help="Input SQLite file")
    parser.add_argument("out_con_string",
                        help="Connection string to empty output database. Example: sqlite:////home/john/out.db")
    args = parser.parse_args()
    print("Arguments given: ")
    print("Take data from: {}".format(args.in_sqlite_file))
    print("Convert to    : {}".format(args.out_con_string))

    # connect to sqlite source database
    con = sqlite3.connect(args.in_sqlite_file)
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("select run_number, started from run_configurations ORDER BY run_number LIMIT 1")

    for row in cur:
        print row["run_number"], row["started"]

    # connect to target DB
    db = ConfigurationProvider(args.out_con_string)
    rcdb.model.Base.metadata.create_all(db.engine)

    # create database
    db.create_run(0)
    db.create_run(1)
    print("Database schema created")

    # select files from old DB
    cur = con.cursor()
    cur.execute("select path, sha256, content from files "
                #"where content LIKE '%<run-end>%' "
                "ORDER BY id DESC ")   # LIMIT 100 OFFSET 2")


    run_count = 0
    for row in cur:
        path = row["path"]
        content = row["content"]
        # add data to database
        run, run_config_file = coda_parser.parse_xml(db, ET.fromstring(content))
        db.add_configuration_file(run, path, content)

        run_count += 1
        print run_count, "\t", path, run, run_config_file


    print "Total {} runs selected".format(run_count)




print "SHA256"
print get_file_sha256("profile.txt")
with open("profile.txt", 'r') as afile:
    text = afile.read()
    print get_string_sha256(text)
