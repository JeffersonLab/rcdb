import argparse
import os
import sqlite3
import sys
from flask import logging
import rcdb.model
from rcdb import ConfigurationProvider
from rcdb import coda_parser
import xml.etree.ElementTree as ET

# setup logger
log = logging.getLogger('rcdb')                     # create run configuration standard logger
log.addHandler(logging.StreamHandler(sys.stdout))   # add console output for logger
log.setLevel(logging.DEBUG)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("con_string", help="Connection string to database")
    args = parser.parse_args()
    print ("create database:")
    print args.con_string

    db = ConfigurationProvider(args.con_string)
    rcdb.model.Base.metadata.create_all(db.engine)

    # create run
    db.create_run(0)
    db.create_run(1)
    print("database created")

    from rcdb.file_archiver import get_file_sha256, get_string_sha256

    con = sqlite3.connect("/home/romanov/gluex/rcdb/experiments.sqlite.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("select run_number, started from run_configurations ORDER BY run_number LIMIT 1")

    for row in cur:
        print row["run_number"], row["started"]


    cur = con.cursor()
    cur.execute("select path, sha256, content from files "
                "where content LIKE '%<run-end>%' "
                "ORDER BY id DESC LIMIT 100 OFFSET 2")

    run_count = 0
    for row in cur:
        path = row["path"]
        content = row["content"]
        run, run_config_file = coda_parser.parse_xml(db, ET.fromstring(content))
        run_count += 1

        print run_count,"\t", path, run, run_config_file


    print "Total {} runs selected".format(run_count)




print "SHA256"
print get_file_sha256("profile.txt")
with open("profile.txt", 'r') as afile:
    text = afile.read()
    print get_string_sha256(text)
