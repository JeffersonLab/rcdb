# This is an advanced example, that illustrates how to use SQLAlchemy Kung fu on RCDB

from rcdb.model import ConditionType, Run, Condition
from rcdb.provider import destroy_all_create_schema, RCDBProvider

from sqlalchemy.orm import joinedload


def make_dummy_db():
    """ Creates inmemory SQLite database"""

    # Create in-memory database
    db = RCDBProvider("sqlite://", check_version=False)
    destroy_all_create_schema(db)

    print("Dummy memory database created!")

    # create conditions types
    event_count_type = db.create_condition_type("event_count", ConditionType.INT_FIELD, "The event count")
    data_value_type = db.create_condition_type("data_value", ConditionType.FLOAT_FIELD, "Some data value")
    tag_type = db.create_condition_type("tag", ConditionType.STRING_FIELD, "Tag... What it means... hm...")

    # create runs and fill values
    for i in range(0, 100):
        run = db.create_run(i)
        db.add_condition(run, event_count_type, i + 950)      # event_count in range 950 - 1049
        db.add_condition(i, data_value_type, (i/100.0) + 1)   # data_value in 1 - 2
        db.add_condition(run, tag_type, "tag" + str(i))       # Some text data

    print("Runs filled with data")
    return db


def querying_using_condition_type(db):
    """ Demonstrates ConditionType query helpers"""
    event_count_type = db.get_condition_type("event_count")
    data_value_type = db.get_condition_type("data_value")

    # select runs where event_count > 1000
    query = event_count_type.run_query \
        .filter(event_count_type.value_field > 1000) \
        .filter(Run.number <= 53)

    print(query.all())

    # select runs where 1.52 < data_value < 1.7
    query2 = data_value_type.run_query \
        .filter(data_value_type.value_field.between(1.52, 1.7)) \
        .filter(Run.number < 55)
    print(query2.all())

    # combine results of this two queries
    print("Results intersect is:")
    print(query.intersect(query2).all())
    print("Results union is:")
    print(query.union(query2).all())


def querying_using_alchemy(db):
    """ Demonstrates SQLAlchemy query helpers"""
    query = db.session.query(Run).join(Run.conditions).join(Condition.type) \
        .filter(Run.number > 1) \
        .filter(((ConditionType.name == "event_count") & (Condition.int_value < 950)) |
                ((ConditionType.name == "data_value") & (Condition.float_value.between(1.52, 1.6)))) \
        .order_by(Run.number)

    print(query.all())


def querying_specific_conditions(db):
    # FIXED QUERY: Using ConditionType.name instead of Condition.name
    query = db.session.query(Condition).join(Condition.run).join(Condition.type) \
        .filter(Run.number > 1, Run.number < 15) \
        .filter(ConditionType.name.in_(["data_value", "event_count"])) \
        .options(joinedload(Condition.run)) \
        .order_by(Condition.type)

    result = query.all()

    # Make sure we have results before trying to print them
    result_length = len(result)
    if result_length == 0:
        print("No conditions found matching the criteria.")
        return

    # Print result pairs
    for row in range(result_length // 2):
        condition1 = result[row*2]
        condition2 = result[row*2 + 1] if row*2 + 1 < result_length else None

        # Get name from the type relationship
        name1 = condition1.type.name if condition1 and condition1.type else "unknown"

        if condition2:
            name2 = condition2.type.name if condition2 and condition2.type else "unknown"
            print(name1, condition1, "\t\t\t", name2, condition2)
        else:
            print(name1, condition1)


if __name__ == "__main__":
    _db = make_dummy_db()

    print("\nquerying_using_condition_type")
    querying_using_condition_type(_db)

    print("\nQuerying_using_alchemy")
    querying_using_alchemy(_db)

    print("\nQuerying_specific_conditions")
    querying_specific_conditions(_db)