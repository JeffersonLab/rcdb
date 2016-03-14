import logging
import os
import sys
from rcdb import ConfigurationProvider
import rcdb.coda_parser


# setup logger
log = logging.getLogger('rcdb')                     # create run configuration standard logger
log.addHandler(logging.StreamHandler(sys.stdout))   # add console output for logger
log.setLevel(logging.DEBUG)                         # print everything. Change to logging.INFO for less output


def print_usage():
    print("""
    Usage:
        parse_coda_log.py <coda_xml_log_file> <db_connection_string>

    <db_connection_string> - is optional. But if it is not set, RCDB_CONNECTION environment variable should be set

    """)


if __name__=="__main__":
    # check we have arguments
    if len(sys.argv) < 2:
        print("ERROR! Please provide a path to xml data file")
        print_usage()
        sys.exit(1)

    # coda xml file name
    coda_xml_log_file = sys.argv[1]

    # connection string
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

    # parse file
    rcdb.coda_parser.parse_file(db, coda_xml_log_file)

