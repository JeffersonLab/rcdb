import os
import rcdb
import argparse

description = """
This script (re)creates empty RCDB database.
If the database already exists, the script CLEARS IT COMPLETELY and creates a fresh empty schema.

THIS SCRIPT IS FOR TESTS ONLY USE alembic TO INITIATE OR UPGRADE THE PRODUCTION DATABASE


"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='A foo that bars')
    parser.add_argument("-c", "--connection", help="Connection string for mysql database")
    parser.add_argument('--i-am-sure', action='store_true', help="Place it to run the script")
    args = parser.parse_args()
    if not args.i_am_sure:
        print("This script CLEARS ALL DATA if the database already exists")
        print("To execute this script please add the flag: ")
        print('  --i-am-sure')
        exit(1)

    print ("creating database:")
    db = rcdb.RCDBProvider(args.connection, check_version=False)
    rcdb.provider.destroy_all_create_schema(db)
    print("database created")
