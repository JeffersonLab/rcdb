
# /home/romanov/ccdb/trunk/scripts/mysql2sqlite/mysql2sqlite.sh -udatmon -hhallddb.jlab.org data_monitoring|sqlite3 sean.db
import argparse
import logging
import sys
import sqlite3
from rcdb import ConfigurationProvider
import rcdb
from rcdb.model import Run

columns_to_import = ["beam_current", "luminosity", "beam_energy", "radiator_type", "solenoid_current", "coherent_peak",
                     "target_type", "collimator_diameter", "status", "ps_converter"]




# setup logger
log = logging.getLogger('rcdb')                     # create run configuration standard logger
log.addHandler(logging.StreamHandler(sys.stdout))   # add console output for logger
log.setLevel(logging.DEBUG)

if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("in_sqlite_file", help="Input SQLite file")
    parser.add_argument("out_con_string",
                        help="Connection string to empty output database. Example: sqlite:////home/john/out.db")
    args = parser.parse_args()
    print("Arguments given: ")
    print("Take data from: {}".format(args.in_sqlite_file))
    print("Convert to    : {}".format(args.out_con_string))


    db = ConfigurationProvider(args.out_con_string)
    event_count_type = db.get_condition_type("event_count")
    print event_count_type

    from rcdb.file_archiver import get_file_sha256, get_string_sha256

    con = sqlite3.connect(args.in_sqlite_file)
    con.row_factory = sqlite3.Row

    #cur = con.cursor()
    #cur.execute("SELECT run_num, num_events,  {} FROM run_info WHERE start_time IS NOT NULL AND run_num < 2472 AND run_num > 742 ORDER BY run_num"
     #           .format(", ".join(columns_to_import)))

    rcdb_cnd_not_found_count = 0
    rcdb_less_count = 0
    rcdb_more_count = 0
    rcdb_only_runs = 0
    seandb_only_runs = 0
    seandb_event_not_found = 0
    seandb_runs_with_positive_events=0
    rcdb_runs_with_positive_events=0
    total = 0
    run_min = 742
    run_max = 2472

    print "rcdb runs", db.session.query(Run).count()

    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM run_info WHERE run_num>={} AND run_num<{}".format(run_min, run_max))
    print "SeanDb runs cur.fetchone()", cur.fetchone()

    for run_number in range(run_min, run_max):
        # read sean db run
        cur = con.cursor()
        cur.execute("SELECT run_num, num_events FROM run_info WHERE run_num={}".format(run_number))
        sdb_run_record = cur.fetchone()



        # red rcdb run
        run = db.get_run(run_number)

        if (not sdb_run_record) and (not run):
            continue

        # if run is in one DB and not in other
        if (not sdb_run_record) and run:
            rcdb_only_runs += 1

        if sdb_run_record and (not run):
            seandb_only_runs += 1

        total += 1

        if (not sdb_run_record) or (not run):
            continue



        if not sdb_run_record["num_events"]:
            print run_number, " event_count is not found in Sean DB"
            seandb_event_not_found += 1
            continue

        sean_events = sdb_run_record["num_events"]
        rcdb_events = db.get_condition(run, event_count_type)
        if not rcdb_events:
            print run_number, " event_count is not found in RCDB"
            rcdb_cnd_not_found_count += 1
            continue

        if rcdb_events.value >=1:
            rcdb_runs_with_positive_events += 1

        if sean_events >= 1:
            seandb_runs_with_positive_events += 1

        if (rcdb_events.value >= 1) and (sean_events >= 1) and (rcdb_events.value != sean_events):

            # rcdb evnets = 0, but Sean DB events = -1
            if (rcdb_events.value == 0) and (sean_events == -1):
                continue

            print ("{} rcdb_events.value '{}' != sean_db_events '{}'".format(run_number, rcdb_events.value, sean_events))
            if rcdb_events.value < sean_events:
                rcdb_less_count += 1
            else:
                rcdb_more_count += 1

    print "rcdb_cnd_not_found_count = ", rcdb_cnd_not_found_count
    print "rcdb_less_count = ", rcdb_less_count
    print "rcdb_more_count = ", rcdb_more_count
    print "rcdb_only_runs = ", rcdb_only_runs
    print "seandb_only_runs = ", seandb_only_runs
    print "seandb_event_not_found = ", seandb_event_not_found
    print "rcdb_runs_with_positive_events=", rcdb_runs_with_positive_events
    print "seandb_runs_with_positive_events=", seandb_runs_with_positive_events
    print "total = ", total





