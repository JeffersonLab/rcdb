import argparse

from sqlalchemy import func

from rcdb import RCDBProvider
from rcdb.model import Condition
from sqlalchemy.orm import aliased

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check RCDB data for errors and fixing it")
    parser.add_argument("-e", "--execute", action="store_true", help="Execute repairs. Fithout the flag script only shows, what is to be done", default=False)
    parser.add_argument("connection", help="RCDB connection string")
    parser.add_argument("-a", "--action", choices=['dbl', 'mpl'], default='dbl')
    args = parser.parse_args()

    print(args)

    # Create RCDBProvider object that connects to DB and provide most of the functions
    db = RCDBProvider(args.connection)
    cts = db.get_condition_types()

    bad_runs_count = 0

    for run in db.get_runs(10000, 20000):
        run_is_printed = False      # To print a run number if error is found
        run.get_condition()

        for ct in cts:
            cnd_count = db.session.query(func.count(Condition.id))\
                .filter(Condition.type == ct, Condition.run == run).scalar()

            if cnd_count > 1:
                if not run_is_printed:
                    print
                    print
                    print "Run = {:<6}, started={}".format(run.number, run.start_time)
                    run_is_printed = True
                    bad_runs_count += 1

                print "   {:<20}: count {} ".format(ct.name, cnd_count)
                conditions = db.session.query(Condition)\
                    .filter(Condition.type == ct, Condition.run == run).all()

                if conditions[0].value != conditions[1].value:
                    for condition in conditions:
                        print "      id={:<7} date={} value={}"\
                            .format(condition.id, condition.created.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], bad_runs_count if ct.value_type != "json" else "json")

    print "bad_runs_count=", bad_runs_count




