import click

from rcdb.provider import RCDBProvider
from .context import pass_rcdb_context


@click.command()
@click.argument('run_index', required=False)
@click.argument('condition', required=False)
@pass_rcdb_context
def ls(context, run_index, condition):
    """Lists conditions"""

    db = context.db
    assert isinstance(db, RCDBProvider)



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
        print("Run number '{}' is not found in DB".format(run_number))
        exit(1)

    ct = db.get_condition_type(name)

    result = db.get_condition(run, ct)
    if not result:
        return

    condition = result
    print(condition.value)


def show_run_conditions(db, run_number):
    """

    :param db: RCDBProvider to database
    :type db: RCDBProvider
    :param run_number: The run number
    :return:
    """

    run = db.get_run(run_number)
    if not run:
        print("Run number {} is not found in DB".format(run_number))
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
            print("{} = {}".format(condition_type.name, condition.value))
        elif condition_type.value_type == ConditionType.STRING_FIELD:
            print("{} = '{}'".format(condition_type.name, condition.value))
        else:
            # it is something big...
            value = str(condition.value).replace('\n', "")[:50]
            print("{} = ({}){}...".format(condition_type.name, condition_type.value_type, value))
