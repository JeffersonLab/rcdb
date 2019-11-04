import logging
import os
import sys
import argparse
from datetime import datetime
import time
import traceback

import rcdb
from rcdb import ConfigurationProvider, UpdateReasons
from rcdb import coda_parser
from rcdb.log_format import BraceMessage as F

# setup logger
from rcdb.model import ConfigurationFile
from update_coda import update_coda_conditions
from update_roc import add_roc_configuration_files
from update_run_config import update_run_config_conditions
from halld_rcdb.run_config_parser import parse_file as parse_run_config_file

log = logging.getLogger('rcdb')  # create run configuration standard logger
log.addHandler(logging.StreamHandler(sys.stdout))  # add console output for logger
log.setLevel(logging.DEBUG)  # print everything. Change to logging.INFO for less output


# [ -n "$UDL" ] && cMsgCommand -u $UDL  -name run_update_rcdb  -subject Prcdb -type DAQ -text "$1"  -string severity=$2  2>&1 > /tmp/${USER}_cMsgCommand


SECTION_GLOBAL="GLOBAL"
SECTION_TRIGGER="TRIGGER"
SECTION_HEADER="=========================="

section_names = [SECTION_GLOBAL, SECTION_TRIGGER, ]

# noinspection SqlDialectInspection
def get_usage():
    return """
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

    """


def try_set_interprocess_lock():
    """
    Sets fcntl lock, so that it is possible to control other instances running

    :return: True if lock is set. False if other process has locked the file already
    """
    # windows doesn't have fcntl
    # noinspection PyUnresolvedReferences
    import fcntl, os, stat, tempfile

    app_name = 'rcdb_daq_update'  # <-- Customize this value

    # Establish lock file settings
    lf_name = '.{}.lock'.format(app_name)
    lf_path = os.path.join(tempfile.gettempdir(), lf_name)
    lf_flags = os.O_WRONLY | os.O_CREAT
    lf_mode = stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH  # This is 0o222, i.e. 146

    # Create lock file
    # Regarding umask, see https://stackoverflow.com/a/15015748/832230
    umask_original = os.umask(0)
    try:
        lf_fd = os.open(lf_path, lf_flags, lf_mode)
    finally:
        os.umask(umask_original)

    # Try locking the file
    try:
        fcntl.lockf(lf_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except IOError:
        return False


def parse_files():
    # We will use this to identify this process in logs. Is done for investigation of double messages
    script_start_datetime = datetime.now()
    script_start_time = time.time()
    script_name = os.urandom(8).encode('hex')
    script_pid = os.getpid()
    script_ppid = os.getppid()
    script_uid = os.getuid()
    script_start_clock = time.clock()

    description = "The script updates RCDB gathering different sources given in --update flag:" \
                  "   coda   - information from coda file (file is required anyway to get run)" \
                  "   config - run configuration file in HallD format" \
                  "   roc    - roc configuration files (taken from run configuration file)"\
                  "            this option is run only if config is given"\
                  "   epics  - epics variables" \
                  "So now update of everything looks like: --update=coda,config,roc,epics" \


    parser = argparse.ArgumentParser(description=description, usage=get_usage())
    parser.add_argument("coda_xml_log_file", help="Path to CODA run log file")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("--reason", help="Reason of the update. 'start', 'update', 'end' or ''", default="")
    parser.add_argument("--update", help="Comma separated, modules to update", default="")
    parser.add_argument("-c", "--connection", help="The connection string (like mysql://rcdb@localhost/rcdb)")
    parser.add_argument("--udl", help="UDL link to send messages to UDL logging")
    parser.add_argument("--ipl", help="Use inter-process lock, that allows ", action="store_true")
    parser.add_argument("--run-config-file", help="Set custom path to run config file", default="")
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
        parser.print_help()
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

    # Use interprocess lock?
    use_interprocess_lock = args.ipl

    script_info = "'{script_start_datetime}', reason: '{reason}', parts: '{parts}, " \
                  "'pid: '{pid}', ppid: '{ppid}', uid: '{uid}', " \
                  .format(
                        script_start_datetime=script_start_datetime,
                        reason=update_reason,
                        parts=args.update,
                        pid=script_pid,
                        ppid=script_ppid,
                        uid=script_uid)

    # Open DB connection
    db = ConfigurationProvider(con_string)

    # Ensure only one such process is running, to avoid duplicated records. See issues #25 #20 #19 on GitHub
    if use_interprocess_lock:
        lock_success = try_set_interprocess_lock()
        wait_count = 0
        while not lock_success:
            # We failed to obtain the lock. Some other instance of this script is running now.
            if update_reason == UpdateReasons.UPDATE:
                log.info("The other instance is running. Since update_reason = update we just exit")
                exit(0)

            time.sleep(1)
            wait_count += 1
            log.debug(F("{script_name}: Waiting lock for {waited}s", script_name=script_name, waited=wait_count))

            if wait_count > 30:
                log.error(F("The other instance is running. Since this update reason is '{}', "
                            "this instance waited > 10s for the other one to end. But it still holds the lock",
                            update_reason))

                # this is major problem. We'll try send it to DB before exit
                db.add_log_record("",
                                  "'{}': Exit!. The other instance is running. This instance waited > 10s! {}"
                                  .format(
                                      script_name,
                                      script_info), 0)
                exit(1)
            lock_success = try_set_interprocess_lock()

    # >oO DB logging
    db.add_log_record("", "'{}': Start. {}".format(script_name, script_info), 0)

    # Create update context
    update_context = rcdb.UpdateContext(db, update_reason)

    # CODA
    # Parse coda xml and save to DB
    log.debug(F("Parsing coda_xml_log_file='{}'", coda_xml_log_file))

    coda_parse_result = coda_parser.parse_file(coda_xml_log_file)

    run_number = coda_parse_result.run_number

    run_config_file = coda_parse_result.run_config_file
    log.debug(F("Parsed coda_xml_log_file='{}'. run='{}', run_config_file='{}'",
                coda_xml_log_file, run_number, run_config_file))

    # >oO DEBUG log message
    now_clock = time.clock()
    db.add_log_record("", "'{}':Parsed coda_xml_log_file='{}'. run='{}', run_config_file='{}', clocks='{}', time: '{}'"
                      .format(script_name, coda_xml_log_file, run_number, run_config_file, run_number,
                              now_clock - script_start_clock, datetime.now()), run_number)

    # Conditions from coda file save to DB
    if "coda" in update_parts:
        log.debug(F("Adding coda conditions to DB", ))
        update_coda_conditions(update_context, coda_parse_result)
    else:
        log.debug(F("Skipping to add coda conditions to DB. Use --update=...,coda to update it", ))

    update_context.run = db.get_run(run_number)
    if update_context.run is None:
        log.warning(F("No DB record for run '{}' is found! Further updates look impossible"))
        update_context.run = run_number

    # Save coda file to DB
    log.debug(F("Adding coda_xml_log_file to DB", ))
    db.add_configuration_file(run_number, coda_xml_log_file, overwrite=True, importance=ConfigurationFile.IMPORTANCE_HIGH)

    # CONFIGURATION FILES
    # Add run configuration file to DB... if it is run-start update
    if args.run_config_file:
        log.debug(F("Flag --run-config-file is provided. Using this as a path to run_config_file: '{}'",
                    args.run_config_file))
        run_config_file = args.run_config_file

    if update_reason in [UpdateReasons.START, UpdateReasons.UNKNOWN] and "config" in update_parts and run_config_file:
        if os.path.isfile(run_config_file) and os.access(run_config_file, os.R_OK):
            # mmm just save for now
            log.debug(F("Adding run_config_file to DB", ))
            db.add_configuration_file(run_number, run_config_file, importance=ConfigurationFile.IMPORTANCE_HIGH)

            log.debug("Parsing run_config_file")
            run_config_parse_result = parse_run_config_file(run_config_file)

            log.debug("Parsed run_config_file. Updating conditions")
            update_run_config_conditions(update_context, run_config_parse_result)
            log.debug("Updated run_config_file conditions")

            if "roc" in update_parts:
                log.debug("Adding ROC config files...")
                add_roc_configuration_files(update_context, run_config_parse_result)
                log.debug("Done ROC config files!")
        else:
            log.warn("Config file '{}' is missing or is not readable".format(run_config_file))
            if "roc" in update_parts:
                log.warn("Can't parse roc configs because there is no main config")

    # Parse run configuration file and save to DB

    # EPICS
    # Get EPICS variables
    epics_start_clock = time.clock()
    if 'epics' in update_parts and run_number:
        log.debug(F("Performing update_epics.py", ))
        # noinspection PyBroadException
        try:
            import update_epics
            conditions = update_epics.update_rcdb_conds(db, run_number, update_reason)
            epics_end_clock = time.clock()
            # >oO DEBUG log message
            if "beam_current" in conditions:
                db.add_log_record("",
                              "'{}': Update epics. beam_current:'{}', epics_clocks:'{}' clocks:'{}', time: '{}'"
                              .format(script_name, conditions["beam_current"], epics_end_clock - epics_start_clock,
                                      epics_end_clock - script_start_clock, datetime.now()), run_number)

        except Exception as ex:
            log.warn("update_epics.py failure. Impossible to run the script. Internal exception is:\n" + str(ex))
            epics_end_clock = time.clock()

            # >oO DEBUG log message
            db.add_log_record("",
                              "'{}': ERROR update epics. Error type: '{}' message: '{}' trace: '{}' "
                              "||epics_clocks:'{}' clocks:'{}' time: '{}'"
                              .format(script_name, type(ex), ex.message, traceback.format_exc(),
                                      epics_end_clock - epics_start_clock, epics_end_clock - script_start_clock,
                                      datetime.now()), run_number)

    log.debug("End of update")

    # >oO DEBUG log message
    now_clock = time.clock()
    db.add_log_record("",
                      "'{}': End of update. Script proc clocks='{}', wall time: '{}', datetime: '{}'"
                      .format(script_name,
                              now_clock - script_start_clock,
                              time.time() - script_start_time,
                              datetime.now()), run_number)


# entry point
if __name__ == "__main__":
    parse_files()
