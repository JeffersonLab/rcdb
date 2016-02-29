import argparse
from argparse import RawDescriptionHelpFormatter
from os import environ
import sys
from sqlalchemy import desc, asc
from rcdb.model import Run, ConditionType, Condition, all_value_types
from rcdb.provider import RCDBProvider
import logging

help_text = """
rcnd - is Run Configuration Database (RCDB) tool to see and manage the Run Conditions.
Full documentation: https://halldweb1.jlab.org/wiki/index.php/RCDB_conditions_python

To connect to database set RCDB_CONNECTION environment variable or set -c or --connection keys:
  SQLite example: 'sqlite:////home/user_name/file.db'
  MySQL example : 'mysql://rcdb:pwd@gluondb/rcdb'

"""

examples = """

GETTING INFORMATION
0. See stats and condition names:
> rcnd

1. Get all condition names:
> rcnd --list

2. Get all condition values for run 1000:
> rcnd 1000

3. Get event_count for run 1000
> rcnd 1000 event_count


WRITING DATA
0. Creating condition type (need to be done once):
> rcnd --create my_value --type string --description "This is my value"

Where --type is:
    bool, int, float, string - basic types. float is the default
    json - to store arrays or custom objects
    time - to store just time. (You can alwais add time information to any other type)
    blob - binary blob. Don't use it if possible

Names policy:
    a. Don't use spaces. Use '_' instead
    b. Full words are better. So 'event_count' is better than evt_cnt
    c. Max name is 255 character. But please, make them shorter

1. Write value for the run:
> rcnd --write "value to write" --replace 1000 my_value

Without --replace error is raised, if run 1000 already have different value for 'my_value'
"""


# setup logger
log = logging.getLogger('rcdb')  # create run configuration standard logger
log.addHandler(logging.StreamHandler(sys.stdout))  # add console output for logger
log.setLevel(logging.INFO)


def create_type(db, name, value_type, description):
    """
    Shows condition value for run

    :param db: RCDBProvider to database
    :type db: RCDBProvider
    :param name: Condition type name
    :param value_type: bool, int, float, string, json, time, blob
    :return:
    """
    if not name:
        print("ERROR no type name is given. Provide type name with --create <type name> flag. See --help")
        exit(1)
    db.create_condition_type(name, value_type, description)


def show_value(db, run_number, name):
    """
    Shows condition value for run

    :param db: RCDBProvider to database
    :type db: RCDBProvider
    :param run_number: The run number
    :param name: Condition type name
    :return:
    """

    run = db.get_run(run_number)
    if not run:
        print ("Run number '{}' is not found in DB".format(run_number))
        exit(1)

    ct = db.get_condition_type(name)

    result = db.get_condition(run, ct)
    if not result:
        return

    if ct.is_many_per_run:
        conditions = result
        for condition in conditions:
            print condition.time
            print condition.value
            print
    else:
        condition = result
        print condition.value


def show_run_conditions(db, run_number):
    """

    :param db: RCDBProvider to database
    :type db: RCDBProvider
    :param run:
    :return:
    """

    run = db.get_run(run_number)
    if not run:
        print ("Run number {} is not found in DB".format(run_number))
        exit(1)

    conditions = db.session.query(Condition).join(Run).join(ConditionType) \
        .order_by(asc(ConditionType.name)) \
        .filter(Run.number == run_number) \
        .all()

    for condition in conditions:
        condition_type = condition.type

        if condition_type.value_type in [ConditionType.INT_FIELD,
                                         ConditionType.BOOL_FIELD,
                                         ConditionType.FLOAT_FIELD]:
            print "{} = {}".format(condition_type.name, condition.value)
        elif condition_type.value_type == ConditionType.STRING_FIELD:
            print "{} = '{}'".format(condition_type.name, condition.value)
        else:
            # it is something big...
            value = str(condition.value).replace('\n', "")[:50]
            print "{} = ({}){}...".format(condition_type.name, condition_type.value_type, value)


def list_all_condition_types(db, extended=False, prefix=""):
    """
    Lists all condition_types in database

    :param db: RCDBProvider to database
    :type db: RCDBProvider
    :return:
    """
    condition_types = db.session.query(ConditionType).order_by(asc(ConditionType.name)).all()
    for condition_type in condition_types:
        assert (isinstance(condition_type, ConditionType))
        if extended:
            line = "{}{} ({}) {}".format(prefix, condition_type.name,
                                         condition_type.value_type,
                                         ' - ' + condition_type.description if condition_type.description else '')
        else:
            line = "{}{}".format(prefix, condition_type.name)

        print line


def print_stats(db):
    """
    Shows the statistics of the database

    :param db:
    :type db: RCDBProvider
    :return:
    """
    run_query = db.session.query(Run)
    condition_type_query = db.session.query(ConditionType)
    print("Runs total: {}".format(run_query.count()))
    print("Last run  : {}".format(run_query.order_by(desc(Run.number)).first().number))
    print("Condition types total: {}".format(condition_type_query.count()))
    print("Conditions: ")
    print("")
    list_all_condition_types(db, False, "  ")


def write_value(db, run_number, name, value, replace):
    """
    Writes value to the run

    :param db: RCDBProvider to database
    :type db: RCDBProvider
    :param run_number: The run number
    :param name: Condition type name
    :return:
    """

    run = db.get_run(run_number)
    if not run:
        print ("Run number '{}' is not found in DB".format(run_number))
        exit(1)

    ct = db.get_condition_type(name)
    db.add_condition(run, ct, value, None, replace)
    print ("Written '{}' to run number {}".format(name, run_number))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=help_text, epilog=examples,
                                     formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("-c", "--connection", help="Connection string to database", metavar='<srting>', default="")
    parser.add_argument("-v", "--verbose", help="Show detailed information about script actions", action='store_true')
    parser.add_argument("-l", "--list", help="List condition names, types and description", action='store_true')
    parser.add_argument("--create", help="Create condition with this name", metavar='<name>', default="")
    parser.add_argument("--type", type=str, help="Set condition type (for --create)", choices=all_value_types,
                        default=ConditionType.FLOAT_FIELD)
    parser.add_argument("-d", "--description", help="Description", default="")
    parser.add_argument("--write", type=str, help="Writes value for the run", metavar='<value>', default="")
    parser.add_argument("--replace", action='store_true', help="Replaces old values if exists (works with --write)")

    parser.add_argument("--list-names", help="List condition names", action='store_true')
    parser.add_argument("run_number", help="The run number", default=-1, type=int, nargs='?')
    parser.add_argument("condition_name", help="Condition name", default="", nargs='?')
    args = parser.parse_args()

    # Set log level
    if args.verbose:
        log.setLevel(logging.DEBUG)
        log.debug("Arguments parsed: ")
        log.debug("  verbose       : ".format(args.verbose))
        log.debug("  connection    : ".format(args.connection))
        log.debug("  run_number    : ".format(args.run_number))
        log.debug("  condition_name: ".format(args.condition_name))
        log.debug("  list-names    : ".format(args.list_names))
        log.debug("  list          : ".format(args.list))
        log.debug("  create        : ".format(args.create))
        log.debug("  type          : ".format(args.type))
        log.debug("  description   : ".format(args.description))
        log.debug("  write         : ".format(args.write))
        log.debug("  replace       : ".format(args.replace))
        # log.debug("  : ".format(args.))

    # Getting connection string
    connection_string = args.connection
    if not connection_string:
        if "RCDB_CONNECTION" in environ.keys():
            connection_string = environ["RCDB_CONNECTION"]
            log.debug("Connection string '{}' taken from RCDB_CONNECTION environment".format(connection_string))
        else:
            print("ERROR. Connection string is not set. "
                  "To connect to database set RCDB_CONNECTION environment variable or set -c or --connection keys")
            exit(1)
    else:
        log.debug("Connection string '{}' taken from arguments".format(connection_string))

    # Connect
    log.debug("Opening database")
    db = RCDBProvider(connection_string)
    log.debug("Opened! (But still no data has been transferred)")

    # CHOOSE ACTION

    # List names only
    if args.list_names:
        log.debug("Listing names only")
        list_all_condition_types(db)
        exit(0)

    # List all condition types with additional info
    if args.list:
        log.debug("Listing conditions ")
        list_all_condition_types(db, True)
        exit(0)

    # Write value to the run
    if args.write:
        log.debug("Write value to the run")
        write_value(db, args.run_number, args.condition_name, args.write, args.replace)
        exit(0)

    # Create a condition type
    if args.create:
        log.debug("Create a condition type")
        create_type(db, args.create, args.type, args.description)
        exit(0)

    # List all conditions for the run
    if args.run_number != -1 and not args.condition_name:
        log.debug("run_number given, no condition_name. Show conditions for run")
        show_run_conditions(db, args.run_number)
        exit(0)

    # Get condition value
    if args.run_number != -1 and args.condition_name:
        log.debug("run_number given, condition_name given. Show condition value for run")
        show_value(db, args.run_number, args.condition_name)
        exit(0)


    # Print stats?
    if args.run_number == -1 and not args.condition_name:
        log.debug("No run_number, no condition_name. Show stats")
        print_stats(db)
        exit(0)


