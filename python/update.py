import sys, os
import xml.etree.ElementTree as ET
import logging
import rcdb

from rcdb.log_format import BraceMessage as lf
from rcdb import ConfigurationProvider
from rcdb import coda_parser

from datetime import datetime


# setup logger
from update_coda import update_coda_conditions

log = logging.getLogger('rcdb')               # create run configuration standard logger
log.addHandler(logging.StreamHandler(sys.stdout))    # add console output for logger
log.setLevel(logging.DEBUG)                           # print everything. Change to logging.INFO for less output

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

        flags:
            --verbose - sets log level to logging.DEBUG (default is logging.INFO)
            --modules=<module1,module2,...> - adds modules to call (example: --modules=update_epics)
            --udl=<udl> - sets UDL link to sent warnings to


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

    must_update_epics = True if "--update=epics,coda" in sys.argv else False
    log.setLevel(logging.DEBUG if "--verbose" in sys.argv else logging.INFO)

    update_reason = ""

    if "--reason=start" in sys.argv:
        update_reason = 'start'
    if "--reason=update" in sys.argv:
        update_reason = 'update'
    if "--reason=end" in sys.argv:
        update_reason = 'end'

    # Open DB connection
    db = ConfigurationProvider(con_string)

    # Create update context
    update_context = rcdb.UpdateContext(db, update_reason)

    # Parse coda xml and save to DB
    log.debug(lf("Parsing coda_xml_log_file='{}'", coda_xml_log_file))
    coda_parse_result = coda_parser.parse_file(coda_xml_log_file)

    run_number = coda_parse_result.run_number
    run_config_file = coda_parse_result.run_config_file
    log.debug(lf("Parsed coda_xml_log_file='{}'. run='{}', run_config_file='{}'",
                 coda_xml_log_file, run_number, run_config_file))

    # Conditions from coda file save to DB
    update_coda_conditions(update_context, coda_parse_result)

    # Save coda file to DB
    log.debug(lf("Adding coda_xml_log_file to DB", ))
    db.add_configuration_file(run_number, coda_xml_log_file, overwrite=True)

    log.debug(lf("Adding run_config_file to DB", ))
    # Parse run configuration file and save to DB
    if run_config_file:
        if os.path.isfile(run_config_file) and os.access(run_config_file, os.R_OK):
            # mmm just save for now
            db.add_configuration_file(run_number, run_config_file)
        else:
            log.warn("Config file '{}' is missing or is not readable".format(run_config_file))

    # Get EPICS variables
    if must_update_epics and run_number:
        log.debug(lf("Performing update_epics.py", ))
        # noinspection PyBroadException
        try:
            import update_epics
            update_epics.update_rcdb_conds(db, run_number)
        except Exception as ex:
            log.warn("update_epics.py failure. Impossible to run the script. Internal exception is:\n" + str(ex))


# entry point
if __name__ == "__main__":
    parse_files()
