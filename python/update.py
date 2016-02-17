import sys, os
import xml.etree.ElementTree as ET
import logging
import rcdb

from rcdb.log_format import BraceMessage as lf
from rcdb import ConfigurationProvider
from rcdb import coda_parser

from datetime import datetime


# setup logger
log = logging.getLogger('rcdb.update')               # create run configuration standard logger
log.addHandler(logging.StreamHandler(sys.stdout))    # add console output for logger
log.setLevel(logging.INFO)                           # print everything. Change to logging.INFO for less output

# [ -n "$UDL" ] && cMsgCommand -u $UDL  -name run_update_rcdb  -subject Prcdb -type DAQ -text "$1"  -string severity=$2  2>&1 > /tmp/${USER}_cMsgCommand


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
    log.setLevel(logging.DEBUG if "--verbose" in sys.argv else logging.INFO)

    # Open DB connection
    db = ConfigurationProvider(con_string)

    # Parse coda xml and save to DB
    log.debug(lf("Parsing coda_xml_log_file='{}'", coda_xml_log_file))

    run, run_config_file = coda_parser.parse_file(db, coda_xml_log_file)
    log.debug(lf("Parsed coda_xml_log_file='{}'. run='{}', run_config_file='{}'", coda_xml_log_file, run, run_config_file))

    log.debug(lf("Adding coda_xml_log_file to DB", ))
    db.add_configuration_file(run, coda_xml_log_file, overwrite=True)

    log.debug(lf("Adding run_config_file to DB", ))
    # Parse run configuration file and save to DB
    if run_config_file:
        if os.path.isfile(run_config_file) and os.access(run_config_file, os.R_OK):
            # mmm just save for now
            db.add_configuration_file(run, run_config_file)
        else:
            log.warn("Config file '{}' is missing or is not readable".format(run_config_file))

    # Get EPICS variables
    if must_update_epics and run:
        log.debug(lf("Performing update_epics.py", ))
        # noinspection PyBroadException
        try:
            import update_epics
            update_epics.update_rcdb_conds(db, run)
        except Exception as ex:
            log.warn("update_epics.py failure. Impossible to run the script. Internal exception is:\n" + str(ex))


# entry point
if __name__ == "__main__":
    parse_files()
