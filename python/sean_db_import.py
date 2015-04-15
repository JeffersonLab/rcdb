
# /home/romanov/ccdb/trunk/scripts/mysql2sqlite/mysql2sqlite.sh -udatmon -hhallddb.jlab.org data_monitoring|sqlite3 sean.db
import argparse
import logging
import sys
import sqlite3
from rcdb import ConfigurationProvider, DefaultConditions
from rcdb.model import ConditionType
import rcdb
from rcdb.model import Run
from rcdb.file_archiver import get_file_sha256, get_string_sha256


columns_to_import = {
  "beam_current": ConditionType.FLOAT_FIELD,
  "luminosity": ConditionType.FLOAT_FIELD,
  "beam_energy": ConditionType.FLOAT_FIELD,
  "radiator_type": ConditionType.STRING_FIELD,
  "solenoid_current": ConditionType.FLOAT_FIELD,
  "coherent_peak": ConditionType.FLOAT_FIELD,
  "target_type": ConditionType.STRING_FIELD,
  "status": ConditionType.INT_FIELD,
  "collimator_diameter": ConditionType.STRING_FIELD,
  "ps_converter": ConditionType.STRING_FIELD
}

# setup logger
log = logging.getLogger('rcdb')                     # create run configuration standard logger
log.addHandler(logging.StreamHandler(sys.stdout))   # add console output for logger
log.setLevel(logging.DEBUG)

if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("in_sqlite_file", help="Input SeanDB SQLite file")
    parser.add_argument("out_con_string",
                        help="Connection string to empty output database. Example: sqlite:////home/john/out.db")
    args = parser.parse_args()
    print("Arguments given: ")
    print("Take data from: {}".format(args.in_sqlite_file))
    print("Convert to    : {}".format(args.out_con_string))

    # open RCDB database
    db = ConfigurationProvider(args.out_con_string)
    event_count_type = db.get_condition_type("event_count")
    print event_count_type

    # open sean db sqlite
    con = sqlite3.connect(args.in_sqlite_file)
    con.row_factory = sqlite3.Row

    # create conditions
    for cnd_name, cnd_type in columns_to_import.iteritems():
        db.create_condition_type(cnd_name, cnd_type, False)
    db.create_condition_type("seandb_event_count", ConditionType.INT_FIELD, False)

    total = 0
    run_min = 742
    run_max = 2472

    for run_number in range(run_min, run_max):
        # read sean db run
        cur = con.cursor()
        cur.execute("SELECT * FROM run_info WHERE run_num={}".format(run_number))
        sdb_run_record = cur.fetchone()

        # ensure run exists in RCDB
        run = db.create_run(run_number)

        if not sdb_run_record or not sdb_run_record["num_events"]:  # no such run in SeanDB
            print "skipped run {}".format(run_number)
            continue

        total += 1

        # cycle through condition types
        for cnd_name, cnd_type in columns_to_import.iteritems():

            if cnd_type == ConditionType.FLOAT_FIELD:
                value = float(sdb_run_record[cnd_name]) if sdb_run_record[cnd_name] else 0.0
            elif cnd_type == ConditionType.INT_FIELD:
                value = int(sdb_run_record[cnd_name]) if sdb_run_record[cnd_name] else 0
            else:
                value = sdb_run_record[cnd_name]

            db.add_condition(run_number, cnd_name, value, replace=True)

        # event number
        event_count = int(sdb_run_record["num_events"])
        db.add_condition(run_number, "seandb_event_count", event_count, replace=True)
        db.add_condition(run_number, DefaultConditions.EVENT_COUNT, event_count, replace=True)

        print "done run {}".format(run_number)

    print ("Total {} runs converted".format(total))