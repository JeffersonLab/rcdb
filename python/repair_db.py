import argparse

from sqlalchemy import func

from rcdb import RCDBProvider
from rcdb.model import Condition, ConditionType
from sqlalchemy.orm import aliased

def fix_double_runs(db, execute):
    cts = db.get_condition_types()

    bad_runs_count = 0
    bad_runs_with_valid_end_count = 0;

    for run in db.get_runs(10000, 20000):
        run_is_printed = False  # To print a run number if error is found
        is_valid_run_end = run.get_condition_value("is_valid_run_end")

        for ct in cts:
            cnd_count = db.session.query(func.count(Condition.id)) \
                .filter(Condition.type == ct, Condition.run == run).scalar()

            if cnd_count > 1:
                if not run_is_printed:
                    print
                    print
                    print "Run = {:<6}, started={} is_valid_run_end={}".format(run.number, run.start_time, is_valid_run_end)
                    run_is_printed = True
                    bad_runs_count += 1
                    if is_valid_run_end:
                        bad_runs_with_valid_end_count += 1

                print "   {:<20}: count {} ".format(ct.name, cnd_count)
                conditions = db.session.query(Condition) \
                    .filter(Condition.type == ct, Condition.run == run).order_by(Condition.id).all()

                if (conditions[0].type.value_type == ConditionType.FLOAT_FIELD and (
                    abs(conditions[0].value - conditions[1].value) < 1e-2)) \
                        or conditions[0].value != conditions[1].value:

                    for condition in conditions:
                        print "      id={:<7} date={} value={}" \
                            .format(condition.id, condition.created.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                                    condition.value if ct.value_type != "json" else "json")

                if execute:
                    print "      deleting ", conditions[1]
                    db.session.delete(conditions[1])
                    db.session.commit()

    print "bad_runs_count=", bad_runs_count, "bad_runs_with_valid_end_count=", bad_runs_with_valid_end_count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check RCDB data for errors and fixing it")
    parser.add_argument("-e", "--execute", action="store_true",
                        help="Execute repairs. Fithout the flag script only shows, what is to be done", default=False)
    parser.add_argument("connection", help="RCDB connection string")
    parser.add_argument("-a", "--action", choices=['dbl', 'mpl'], default='dbl')
    args = parser.parse_args()

    print(args)

    # Create RCDBProvider object that connects to DB and provide most of the functions
    db = RCDBProvider(args.connection)

    if args.action == 'dbl':
        fix_double_runs(db, args.execute)

    ct = db.get_condition_type("target_type")
    target_types = db.session.query(Condition.text_value).filter(Condition.type == ct).distinct().all()
    for target_type, in target_types:
        print str(target_type)

