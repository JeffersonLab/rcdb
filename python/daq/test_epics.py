import logging
import sys
from pprint import pprint
from update_epics import setup_run_conds, update_beam_conditions
import rcdb

if __name__ == "__main__":
    log = logging.getLogger('rcdb')
    log.addHandler(logging.StreamHandler(sys.stdout))    # add console output for logger
    log.setLevel(logging.DEBUG)                          # print everything. Change to logging.INFO for less output

    db = rcdb.RCDBProvider("mysql://rcdb@hallddb.jlab.org/rcdb")
    run = db.get_run(120080)
    #conditions = update_beam_conditions(run)
    conditions = setup_run_conds(run)
    pprint(conditions)

    #query = db.session.query(Run).filter(Run.number > 9999)
    #print(query.all())
    #for run in query.all():
    #    update_rcdb_conds(db, run.number)