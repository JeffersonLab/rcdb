import argparse

from sqlalchemy import func

from rcdb import RCDBProvider
from rcdb.model import Condition, ConditionType


def fix_double_runs(db, execute):
    cts = db.get_condition_types()

    bad_runs_count = 0
    bad_runs_with_valid_end_count = 0

    for run in db.get_runs(10000, 20000):
        run_is_printed = False  # To print a run number if error is found
        is_valid_run_end = run.get_condition_value("is_valid_run_end")

        for ct in cts:
            cnd_count = db.session.query(func.count(Condition.id)) \
                .filter(Condition.type == ct, Condition.run == run).scalar()

            if cnd_count > 1:
                if not run_is_printed:
                    print("Run = {:<6}, started={} is_valid_run_end={}".format(run.number, run.start_time, is_valid_run_end))
                    run_is_printed = True
                    bad_runs_count += 1
                    if is_valid_run_end:
                        bad_runs_with_valid_end_count += 1

                print("   {:<20}: count {} ".format(ct.name, cnd_count))
                conditions = db.session.query(Condition) \
                    .filter(Condition.type == ct, Condition.run == run).order_by(Condition.id).all()

                if (conditions[0].type.value_type == ConditionType.FLOAT_FIELD and (
                    abs(conditions[0].value - conditions[1].value) < 1e-2)) \
                        or conditions[0].value != conditions[1].value:

                    for condition in conditions:
                        print ("      id={:<7} date={} value={}" \
                            .format(condition.id, condition.created.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                                    condition.value if ct.value_type != "json" else "json"))

                if execute:
                    print("      deleting ", conditions[1])
                    db.session.delete(conditions[1])
                    db.session.commit()

    print ("bad_runs_count=", bad_runs_count, "bad_runs_with_valid_end_count=", bad_runs_with_valid_end_count)


def fix_no_daq_run(db, execute):
    result = db.select_runs()
    daq_run_values = result.get_values(['daq_run'])
    print ("Runs with daq_run==None")
    print ("Run       Started")
    print ("===========================================")
    for i, run in enumerate(result):
        if daq_run_values[i][0] is None:
            print ("{:<10}{}".format(run.number, run.start_time))
            if execute:
                db.add_condition(run, "daq_run", "EXPERT", auto_commit=False)
    print ("===========================================")

    if execute:
        print ("Committing to DB")
        db.session.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check RCDB data for errors and fixing it")
    parser.add_argument("-e", "--execute", action="store_true",
                        help="Execute repairs. Fithout the flag script only shows, what is to be done", default=False)
    parser.add_argument("connection", help="RCDB connection string")
    parser.add_argument("-a", "--action", choices=['dbl', 'mpl', 'no_daq_run'], default='dbl')
    args = parser.parse_args()

    print(args)

    # Create RCDBProvider object that connects to DB and provide most of the functions
    db = RCDBProvider(args.connection)

    if args.action == 'dbl':
        fix_double_runs(db, args.execute)
    elif args.action == 'no_daq_run':
        fix_no_daq_run(db, args.execute)
