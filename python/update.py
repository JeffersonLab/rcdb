import sys, os
import xml.etree.ElementTree as ET
import logging
import rcdb

from rcdb.log_format import BraceMessage as lf
from rcdb import ConfigurationProvider
from rcdb import coda_parser

from datetime import datetime


# setup logger
log = logging.getLogger('rcdb')                     # create run configuration standard logger
log.addHandler(logging.StreamHandler(sys.stdout))   # add console output for logger
log.setLevel(logging.INFO)                          # print everything. Change to logging.INFO for less output


# noinspection SqlDialectInspection
def print_usage():
    print("""
    Usage:
        minimal:
            update.py <coda_xml_log_file>

            update.py <coda_xml_log_file> <db_connection_string> <modules>

        full:


        example:
            # parses current_run.log, uses RCDB_CONNECTION env. variable to determine con string
            # doesnt update epics conditions nor other optional modules are uses
            update.py current_run.log

            # connection string is given, update_epics.py is called after completion of main parsing
            update.py current_run.log mysql://rcdb@localhost/rcdb  --modules=update_epics


    <db_connection_string> - is optional. But if it is not set, RCDB_CONNECTION environment variable should be set

    """)




def parse_files():
    # check we have arguments
    if len(sys.argv) < 2:
        print("ERROR! Please provide a path to xml data file")
        print_usage()
        sys.exit(1)

    # coda xml file name
    coda_xml_log_file = sys.argv[1]

    # Connection string
    if "RCDB_CONNECTION" in os.environ:
        con_string = os.environ["RCDB_CONNECTION"]
    else:
        print ("ERROR! RCDB_CONNECTION is not set and is not given as a parameter")
        print_usage()
        sys.exit(2)

    must_update_epics = True if "--modules=update_epics" in sys.argv else False


    # Open DB connection
    db = ConfigurationProvider(con_string)

    # Parse coda xml and save to DB
    run, run_config_file = coda_parser.parse_file(db, coda_xml_log_file)
    db.add_configuration_file(run, coda_xml_log_file, overwrite=True)

    # Parse run configuration file and save to DB
    if run_config_file:
        if os.path.isfile(run_config_file) and os.access(run_config_file, os.R_OK):
            # mmm just save for now
            db.add_configuration_file(run, run_config_file)
        else:
            log.warn("Config file '{}' is missing or is not readable".format(run_config_file))

    # Get EPICS variables
    if must_update_epics and run:
        # noinspection PyBroadException
        try:
            import update_epics
            update_epics.update_rcdb_conds(db, run)
        except Exception as ex:
            log.warn("update_epics.py failure. Impossible to run the script. Internal exception is:\n" + str(ex))


# entry point
if __name__ == "__main__":
    #import argparse
    #parser = argparse.ArgumentParser()
    #args = parser.parse_args()
    #print args.echo

    parse_files()
