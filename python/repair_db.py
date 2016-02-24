import argparse

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
    for ct in cts:
        print ct, ct.is_many_per_run

        cnd_left = aliased(Condition)
        cnd_right = aliased(Condition)

        query = db.session.query(cnd_left, cnd_right)\
            .filter(cnd_left.condition_type == ct)

            if i != 0:
                query = query.filter(alias_cnd.run_number == aliased_cnd[0].run_number)

        query = query.filter(aliased_cnd[0].run_number >= run_min, aliased_cnd[0].run_number <= run_max)\
            .join(aliased_cnd[0].run)

