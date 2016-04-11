import logging
import os
import sys
import argparse

import rcdb
from rcdb import ConfigurationProvider, UpdateReasons
from rcdb import coda_parser
from rcdb.log_format import BraceMessage as F

# setup logger
from update_coda import update_coda_conditions

log = logging.getLogger('rcdb')                     # create run configuration standard logger
log.addHandler(logging.StreamHandler(sys.stdout))   # add console output for logger
log.setLevel(logging.DEBUG)                         # print everything. Change to logging.INFO for less output

# [ -n "$UDL" ] && cMsgCommand -u $UDL  -name run_update_rcdb  -subject Prcdb -type DAQ -text "$1"  -string severity=$2  2>&1 > /tmp/${USER}_cMsgCommand


# noinspection SqlDialectInspection
def print_usage():
    print("""
    Usage:
        minimal:
            update.py <coda_xml_log_file>

            update.py <coda_xml_log_file> -c <db_connection_string> --update=<modules> --reason=[start,update,end]

        full:


        example:
            # parses current_run.log, uses RCDB_CONNECTION env. variable to determine con string
            # doesnt update EPICS values nor other optional data
            update.py current_run.log

            # connection string is given, update_epics.py is called after completion of main parsing
            update.py current_run.log -c mysql://rcdb@localhost/rcdb  --update=epics,coda --reason=start

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

    parser = argparse.ArgumentParser()
    parser.add_argument("coda_xml_log_file", help="Path to CODA run log file")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("--reason", help="Reason of the update. 'start', 'update', 'end' or ''", default="")
    parser.add_argument("--update", help="Comma separated, modules to update", default="")
    parser.add_argument("-c", "--connection", help="The connection string (like mysql://rcdb@localhost/rcdb)")
    args = parser.parse_args()

    # Figure out the parameters
    log.setLevel(logging.DEBUG if args.verbose else logging.INFO)

    # coda xml file name
    coda_xml_log_file = args.coda_xml_log_file
    log.debug(F("coda_xml_log_file = '{}'", coda_xml_log_file))

    # Connection string
    if args.connection:
        con_string = args.connection
    elif "RCDB_CONNECTION" in os.environ:
        con_string = os.environ["RCDB_CONNECTION"]
    else:
        print ("ERROR! RCDB_CONNECTION is not set and is not given as a script parameter (-c)")
        print_usage()
        sys.exit(2)
    log.debug(F("con_string = '{}'", con_string))

    # What to update
    update_parts = []
    if args.update:
        update_parts = args.update.split(',')
    log.debug(F("update_parts = {}", update_parts))

    # Update reason
    update_reason = args.reason
    log.debug(F("update_reason = '{}'", update_reason))

    # Open DB connection
    db = ConfigurationProvider(con_string)

    # Create update context
    update_context = rcdb.UpdateContext(db, update_reason)

    # Parse coda xml and save to DB
    log.debug(F("Parsing coda_xml_log_file='{}'", coda_xml_log_file))

    coda_parse_result = coda_parser.parse_file(coda_xml_log_file)

    run_number = coda_parse_result.run_number
    run_config_file = coda_parse_result.run_config_file
    log.debug(F("Parsed coda_xml_log_file='{}'. run='{}', run_config_file='{}'",
                coda_xml_log_file, run_number, run_config_file))

    # Conditions from coda file save to DB
    if "coda" in update_parts:
        log.debug(F("Adding coda conditions to DB", ))
        update_coda_conditions(update_context, coda_parse_result)
    else:
        log.debug(F("Skipping to add coda conditions to DB. Use --update=...,coda to update it", ))

    # Save coda file to DB
    log.debug(F("Adding coda_xml_log_file to DB", ))
    db.add_configuration_file(run_number, coda_xml_log_file, overwrite=True)

    # Add run configuration file to DB... if it is run-start update
    if update_reason == UpdateReasons.START and run_config_file:
        if os.path.isfile(run_config_file) and os.access(run_config_file, os.R_OK):
            # mmm just save for now
            log.debug(F("Adding run_config_file to DB", ))
            db.add_configuration_file(run_number, run_config_file)
        else:
            log.warn("Config file '{}' is missing or is not readable".format(run_config_file))

    # Parse run configuration file and save to DB

    # Get EPICS variables
    if 'epics' in update_parts and run_number:
        log.debug(F("Performing update_epics.py", ))
        # noinspection PyBroadException
        try:
            import update_epics
            update_epics.update_rcdb_conds(db, run_number)
        except Exception as ex:
            log.warn("update_epics.py failure. Impossible to run the script. Internal exception is:\n" + str(ex))

    log.debug("End of update")


# entry point
if __name__ == "__main__":
    parse_files()
