import os
import rcdb
import argparse

description = """
This script (re)creates empty RCDB database.
If the database already exists, the script CLEARS IT COMPLETELY and creates a fresh empty schema.

THIS SCRIPT IS FOR TESTS ONLY USE alembic TO INITIATE OR UPGRADE THE PRODUCTION DATABASE


"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='The utility to create RCDB empty database. '
                                                 'Erases (!) the existing database'
                                     )
    parser.add_argument("-c", "--connection", help="The connection string for mysql database")
    parser.add_argument('--i-am-sure', action='store_true', help="Place it to run the script")
    parser.add_argument('--add-def-con', action='store_true', default=False,
                        help="Add default conditions like run start time, event_count, event_rate")

    args = parser.parse_args()
    if not args.i_am_sure:
        print("This script CLEARS ALL DATA if the database exists")
        print("To execute this script please add the flag: ")
        print('  --i-am-sure')
        print("General usage:")
        parser.print_help()
        parser.print_usage()
        exit(1)

    print ("creating database:")
    db = rcdb.RCDBProvider(args.connection, check_version=False)
    rcdb.provider.destroy_all_create_schema(db)
    print("database created")

    if args.add_def_con:
        rcdb.create_condition_types(db)
        print("default conditions filled")


