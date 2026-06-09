"""
Shared builders for seeding an RCDB database with deterministic test data.

These are used by ``rcdb db init --add-tests`` and ``rcdb db init --add-cpp-tests``
so that ``rcdb db init`` is the single, canonical way to create *and* populate a
SQLite database for testing - replacing the old standalone
``tests/create_test_database.py`` script and the checked-in ``tests/test.sqlite.db``
fixture.

Both functions assume the schema already exists (the caller runs ``db init`` first);
they only add runs, condition types and conditions, then commit.
"""

from datetime import datetime

import rcdb
from rcdb.model import ConditionType


def fill_test_data(db):
    """Seed the generic unit-test dataset (condition types ``a``-``g``).

    Mirrors the table used by ``tests/test_select_values.py``::

        run |   a  |    b     |   c   |   d   |       e       |       f       |        g
        ----+------+----------+-------+-------+---------------+---------------+------------------
          1 | 1    | 1.01     | False | haha  | {"a":1}       | None          | None
          2 | 2    | 2.333... | True  | None  | None          | None          | None
          3 | 3    | 2.55     | True  | None  | None          | None          | None
          4 | 4    | 1.64     | True  | hoho  | [1,2,3]       | my only value | None
          5 | None | 2.32     | False | bang  | None          | None          | aGVsbG8gd29ybGQ=
          9 | 9    | 2.02     | True  | mew   | [3,2,{"b":5}] | None          | None

    :param db: RCDBProvider connected to a database with an existing schema
    :type db: rcdb.RCDBProvider
    """
    assert isinstance(db, rcdb.RCDBProvider)

    # create runs
    for i in range(1, 6):
        db.create_run(i)
    db.create_run(9)

    db.create_condition_type("a", ConditionType.INT_FIELD, "Test condition 'a'")
    db.create_condition_type("b", ConditionType.FLOAT_FIELD, "Test condition 'b'")
    db.create_condition_type("c", ConditionType.BOOL_FIELD, "Test condition 'c'")
    db.create_condition_type("d", ConditionType.STRING_FIELD, "Test condition 'd'")
    db.create_condition_type("e", ConditionType.JSON_FIELD, "Test condition 'e'")
    db.create_condition_type("f", ConditionType.STRING_FIELD, "Test condition 'f'")
    db.create_condition_type("g", ConditionType.BLOB_FIELD, "Test condition 'g'")

    db.add_condition(1, "a", 1)
    db.add_condition(2, "a", 2)
    db.add_condition(3, "a", 3)
    db.add_condition(4, "a", 4)
    db.add_condition(9, "a", 9)

    db.add_condition(1, "b", 1.01)
    db.add_condition(2, "b", 7.0 / 3.0)
    db.add_condition(3, "b", 2.55)
    db.add_condition(4, "b", 1.64)
    db.add_condition(5, "b", 2.32)
    db.add_condition(9, "b", 2.02)

    db.add_condition(1, "c", False)
    db.add_condition(2, "c", True)
    db.add_condition(3, "c", True)
    db.add_condition(4, "c", True)
    db.add_condition(5, "c", False)
    db.add_condition(9, "c", True)

    db.add_condition(1, "d", "haha")
    db.add_condition(4, "d", "hoho")
    db.add_condition(5, "d", "bang")
    db.add_condition(9, "d", "mew")

    db.add_condition(1, "e", '{"a":1}')
    db.add_condition(4, "e", "[1,2,3]")
    db.add_condition(9, "e", '[3,2,{"b":5}]')

    db.add_condition(4, "f", "my only value")

    db.add_condition(5, "g", "aGVsbG8gd29ybGQ=")

    db.session.commit()


def fill_cpp_test_data(db):
    """Seed the fixture the C++ Catch tests expect.

    Reproduces the data that used to live in the checked-in ``tests/test.sqlite.db``
    fixture: one condition type per value type and two runs. The C++ tests
    (``cpp/tests/test_SqLiteProvider.cpp``, ``test_Connection.cpp``) assert that
    run 1 ``int_cnd == 5`` and that a nonexistent run returns no condition.

    :param db: RCDBProvider connected to a database with an existing schema
    :type db: rcdb.RCDBProvider
    """
    assert isinstance(db, rcdb.RCDBProvider)

    db.create_run(1)
    db.create_run(2)

    db.create_condition_type("bool_cnd", ConditionType.BOOL_FIELD, "C++ test bool condition")
    db.create_condition_type("json_cnd", ConditionType.JSON_FIELD, "C++ test json condition")
    db.create_condition_type("string_cnd", ConditionType.STRING_FIELD, "C++ test string condition")
    db.create_condition_type("float_cnd", ConditionType.FLOAT_FIELD, "C++ test float condition")
    db.create_condition_type("int_cnd", ConditionType.INT_FIELD, "C++ test int condition")
    db.create_condition_type("time_cnd", ConditionType.TIME_FIELD, "C++ test time condition")
    db.create_condition_type("blob_cnd", ConditionType.BLOB_FIELD, "C++ test blob condition")

    db.add_condition(1, "bool_cnd", True)
    db.add_condition(2, "bool_cnd", False)

    db.add_condition(1, "json_cnd", '{"firstName":"John", "lastName":"Doe"}')
    db.add_condition(2, "json_cnd", '{"firstName":"Elton", "lastName":"Smith"}')

    db.add_condition(1, "string_cnd", "hey")
    db.add_condition(2, "string_cnd", "ho")

    db.add_condition(1, "float_cnd", 0.1)
    db.add_condition(2, "float_cnd", 2.2)

    db.add_condition(1, "int_cnd", 5)
    db.add_condition(2, "int_cnd", 10)

    db.add_condition(1, "time_cnd", datetime(2016, 3, 11, 0, 59, 9))
    db.add_condition(2, "time_cnd", datetime(2016, 3, 11, 1, 0, 0))

    db.add_condition(1, "blob_cnd", "F4D1")
    db.add_condition(2, "blob_cnd", "1235")

    db.session.commit()
