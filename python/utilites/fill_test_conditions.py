import logging
import os
import sys
import rcdb
import datetime
import random

# setup logger
from rcdb.model import ConditionType

log = logging.getLogger('rcdb')  # create run configuration standard logger
log.addHandler(logging.StreamHandler(sys.stdout))  # add console output for logger
log.setLevel(logging.DEBUG)  # print everything. Change to logging.INFO for less output

if __name__ == '__main__':
    # times
    time_cursor = datetime.datetime(2014, 3, 4, 14, 10)

    # create  and connect to DB
    con_srt = os.environ["RCDB_CONNECTION"] \
        if "RCDB_CONNECTION" in os.environ.keys() \
        else "mysql+mysqlconnector://rcdb@127.0.0.1/rcdb"

    db = rcdb.ConfigurationProvider(con_srt)

    # create several conditions
    events_num_ct = db.create_condition_type("event_count", ConditionType.INT_FIELD, "Number of events in run")
    events_rate_ct = db.create_condition_type("events_rate", ConditionType.FLOAT_FIELD, "Daq events rate")
    temperature_ct = db.create_condition_type("temperature", ConditionType.INT_FIELD, "Temperature of the Sun")

    # create 100 runs
    random.seed(1)
    for run_number in range(1, 101):

        # start and end time
        run_length = random.randrange(10, 600)
        db.add_run_start_time(run_number, time_cursor)
        time_cursor += datetime.timedelta(seconds=run_length)
        db.add_run_end_time(run_number, time_cursor)

        # fill condition values
        events_num = random.randrange(1, 100000)
        db.add_condition(run_number, "event_count", events_num)
        db.add_condition(run_number, events_rate_ct, events_num/float(run_length))
        db.add_condition(run_number, temperature_ct, random.randrange(19, 32))

        time_cursor += datetime.timedelta(minutes=1)   # 1 minute to next run
