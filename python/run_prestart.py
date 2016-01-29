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
log.setLevel(logging.DEBUG)                         # print everything. Change to logging.INFO for less output


def print_usage():
    print("""
    Usage:
        run_prestart <coda_xml_log_file> <db_connection_string>
        run_end      <coda_xml_log_file> <db_connection_string>

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

    if len(sys.argv) > 2:       # RCDB connection string is given
        con_string = sys.argv[2]
    elif "RCDB_CONNECTION" in os.environ:
        con_string = os.environ["RCDB_CONNECTION"]
    else:
        print ("ERROR! RCDB_CONNECTION is not set and is not given as a parameter")
        print_usage()
        sys.exit(2)

    # Open DB connection
    db = ConfigurationProvider(con_string)

    # Parse coda xml and save to DB
    run, run_config_file = coda_parser.parse_file(db, coda_xml_log_file)
    db.add_configuration_file(run, coda_xml_log_file, overwrite=True)

    # Parse run configuration file and save to DB
    if run_config_file:
        # mmm just save for now
        db.add_configuration_file(run, run_config_file)


# entry point
if __name__ == "__main__":
    parse_files()
