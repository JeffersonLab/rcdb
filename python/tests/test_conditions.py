from datetime import datetime
import unittest
import rcdb
import rcdb.model
from rcdb.model import ConditionType, Condition, Run

import logging

#logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)



class TestConditions(unittest.TestCase):
    """ Tests ConditionType, ConditionValue classes and their operations in provider"""

    def setUp(self):
        self.db = rcdb.RCDBProvider("sqlite://")
        rcdb.model.Base.metadata.create_all(self.db.engine)
        # create run
        self.db.create_run(1)

    def tearDown(self):
        self.db.disconnect()

    def test_creating_condition_type(self):
        """Test of create_condition_type function"""

        # Create condition type
        ct = self.db.create_condition_type("test", ConditionType.FLOAT_FIELD, False, description="This is a test")

        # Check values
        self.assertIsInstance(ct, ConditionType)
        self.assertEqual(ct.name, "test")
        self.assertEqual(ct.value_type, ConditionType.FLOAT_FIELD)
        self.assertFalse(ct.is_many_per_run)
        self.assertEqual(ct.description, "This is a test")

        # Creating ConditionType with the same name but different type or flag should raise
        self.assertRaises(rcdb.OverrideConditionTypeError, self.db.create_condition_type, "test",
                          ConditionType.INT_FIELD, False)
        self.assertRaises(rcdb.OverrideConditionTypeError, self.db.create_condition_type, "test",
                          ConditionType.FLOAT_FIELD, True)

        # Creating the same existing ConditionType should not raise
        try:
            self.db.create_condition_type("test", ConditionType.FLOAT_FIELD, False)
        except rcdb.OverrideConditionTypeError:
            self.fail()

    def test_get_condition_type(self):
        """Test of get_condition_type function"""
        # Create condition type
        ct = self.db.create_condition_type("test", ConditionType.FLOAT_FIELD, False)

        # now get it from DB using API
        ct = self.db.get_condition_type("test")
        self.assertEqual(ct.name, "test")

        # now check that there is no way selecting non existent
        self.assertRaises(rcdb.NoConditionTypeFound, self.db.get_condition_type, "abra kadabra")

    def test_basic_work_with_condition_value(self):
        """ Tests add_condition_value funciton
        :return:None
        """
        ct = self.db.create_condition_type("events_num", ConditionType.FLOAT_FIELD, False)
        self.db.add_condition(1, "events_num", 1000)
        result = self.db.get_condition(1, "events_num")
        self.assertEqual(result.value, 1000)


    def test_one_per_run_condition_values(self):
        ct = self.db.create_condition_type("single", ConditionType.INT_FIELD, False)

        # First addition to DB
        val = self.db.add_condition(1, ct, 1000)

        # The func should return ConditionValue it created or found in BD
        self.assertIsNotNone(val)

        # Ok. no exception and do nothing is the very same value already exists
        val = self.db.add_condition(1, "single", 1000)
        self.assertIsNotNone(val)

        # Error. exception ConditionValueExistsError
        self.assertRaises(rcdb.OverrideConditionValueError, self.db.add_condition, 1, "single", 2222)

        # Ok. Replacing existing value
        val = self.db.add_condition(1, "single", 2222, replace=True)
        self.assertIsNotNone(val)

        # Check, that get method works as expected
        val = self.db.get_condition(1, "single")
        self.assertEqual(val.value, 2222)
        self.assertEqual(val.int_value, 2222)
        self.assertIsNone(val.time)

        # Add time information to the
        val = self.db.add_condition(1, "single", 2222, datetime(2015, 10, 10, 15, 28, 12, 111), replace=True)
        self.assertIsNotNone(val)

        # Create condition for non existent run is impossible
        self.assertRaises(rcdb.NoRunFoundError, self.db.add_condition, 1763654, "single", 2222)

    def test_timed_many_per_run_condition_values(self):
        """Test how many conditions per run are saved"""

        # Many condition values allowed for the run (is_many_per_run=True)
        #    1. If run has this condition, with the same value and actual_time the func. DOES NOTHING
        #    2. If run has this conditions but at different time, it adds this condition to DB
        #    3. If run has this condition at this time

        ct = self.db.create_condition_type("multi", ConditionType.INT_FIELD, True)
        time1 = datetime(2015,9,1,14,21,01, 222)
        time2 = datetime(2015,9,1,14,21,01, 333)

        # First addition to DB. Time is None
        self.db.add_condition(1, "multi", 1000)

        # Ok. Do nothing, such value already exists
        self.db.add_condition(1, "multi", 1000)

        # Error. Another value for time None
        self.assertRaises(rcdb.OverrideConditionValueError, self.db.add_condition, 1, "multi", 2222)

        # Ok. Replacing existing value for time None
        self.db.add_condition(1, "multi", 2222, replace=True)

        # Ok. Value for time1 is added to DB
        self.db.add_condition(1, "multi", 3333, time1)

        # Error. Value differs for time1
        self.assertRaises(rcdb.OverrideConditionValueError, self.db.add_condition, 1, "multi", 4444, time1)

        # Ok. Add 444 for time2 to DB
        self.db.add_condition(1, "multi", 4444, time2)

        results = self.db.get_condition(1, "multi")
        # We should get 3 values as:
        # 0: value=2222; time=None
        # 1: value=3333; time=time1
        # 2: value=4444; time=time2
        # lets check it
        self.assertEqual(len(results), 3)
        values = [result.value for result in results]
        times = [result.time for result in results]

        self.assertEqual(values, [2222, 3333, 4444])
        self.assertEqual(times, [None, time1, time2])


    def test_timed_one_per_run_condition_values(self):
        """Test how to work with one_per_run condition values that have time information too"""

        ct = self.db.create_condition_type("timed", ConditionType.INT_FIELD, False)

        time1 = datetime(2015, 9, 1, 14, 21, 01, 222)
        time2 = datetime(2015, 9, 1, 14, 21, 01, 333)

        # First addition to DB
        self.db.add_condition(1, "timed", 1, time1)

        # Ok. Do nothing
        self.db.add_condition(1, "timed", 1, time1)

        # Error. Time is different
        self.assertRaises(rcdb.OverrideConditionValueError, self.db.add_condition, 1, "timed", 1, time2)

        # Error. Value is different
        self.assertRaises(rcdb.OverrideConditionValueError, self.db.add_condition, 1, "timed", 5, time1)

        # Ok. Value replaced
        self.db.add_condition(1, "timed", 5, time2, replace=True)

        val = self.db.get_condition(1, "timed")
        self.assertEqual(val.value, 5)
        self.assertEqual(val.time, time2)

    def test_check_float_condition_value(self):
        """ Tests add_condition_value funciton
        :return:None
        """
        ct = self.db.create_condition_type("float_cnd", ConditionType.FLOAT_FIELD, False)
        cnd = self.db.add_condition(1, ct, 0.15)

        # evict all database-loaded data from the session
        self.db.session.expire_all()

        result = self.db.get_condition(1, "float_cnd")
        self.assertEqual(result.value, 0.15)

    def test_run_link_to_conditions(self):
        """ Tests add_condition_value funciton
        :return:None
        """
        ct = self.db.create_condition_type("one", ConditionType.INT_FIELD, False)
        self.db.add_condition(1, "one", 1000)
        ct = self.db.create_condition_type("two", ConditionType.INT_FIELD, False)
        self.db.add_condition(1, "two", 2000)

        run = self.db.get_run(1)

        self.assertGreaterEqual(len(run.conditions),  2)
        names = [condition.name for condition in run.conditions]
        self.assertIn("one", names)
        self.assertIn("two", names)

    def test_query(self):
        """ Tests add_condition_value function
        :return:None
        """
        ct = self.db.create_condition_type("one", ConditionType.INT_FIELD, False)
        ct = self.db.create_condition_type("two", ConditionType.INT_FIELD, False)

        for i in range(101, 110):
            self.db.create_run(i)
            self.db.add_condition(i, "one", (i-100)*10)
            print self.db.add_condition(i, "two", (i-100)*100).int_value


        print ct.run_query.filter(ct.value_field > 300).filter(ct.value_field < 900).all()


        print self.db.session.query(Run).join(Run.conditions).filter((Condition.type == ct) & (Condition.int_value < 200)).all()

        runs = self.db.session.query(Run).join(Run.conditions).join(Condition.type)\
            .filter(Run.number > 105)\
            .filter(((ConditionType.name == "two") & (Condition.int_value < 900)) | ((ConditionType.name == "one") & (Condition.int_value > 200)))

        print type(ConditionType.name == "haha")

        print str(runs)

        print runs.all()

    def test_usage_of_string_values(self):
        self.db.create_condition_type("string_val", ConditionType.STRING_FIELD, False)
        self.db.add_condition(1, "string_val", "test test")
        val = self.db.get_condition(1, "string_val")
        self.assertEqual(val.value, "test test")

    def test_time_only_condition(self):
        """Test how to work with time information too"""

        self.db.create_condition_type("lunch_bell_rang", ConditionType.TIME_FIELD, False)

        # add value to run 1
        time = datetime(2015, 9, 1, 14, 21, 01)
        self.db.add_condition(1, "lunch_bell_rang", time)

        # get from DB
        val = self.db.get_condition(1, "lunch_bell_rang")
        self.assertEqual(val.value, time)
        self.assertEqual(val.time, time)
        print val.value

    def test_use_run_instead_of_run_number(self):

        run = self.db.create_run(2)
        ct = self.db.create_condition_type("lalala", ConditionType.INT_FIELD, False)
        val = self.db.add_condition(run, ct, 10)      # event_count in range 950 - 1049

        self.assertEqual(val.run_number, 2)

    def test_auto_commit_false(self):
        """ Test auto_commit feature that allows to commit changes to DB later and"""
        ct = self.db.create_condition_type("ac", ConditionType.INT_FIELD, False)

        # Add condition to addition but don't commit changes
        self.db.add_condition(1, ct, 10, auto_commit=False)

        # But the object is selectable already
        val = self.db.get_condition(1, ct)
        self.assertEqual(val.value, 10)

        # Commit session. Now "ac"=10 is stored in the DB
        self.db.session.commit()

        # Now we deffer committing changes to DB. Object is in SQLAlchemy cache
        self.db.add_condition(1, ct, 20, None, True, False)
        self.db.add_condition(1, ct, 30, None, True, False)

        # If we select this object, SQLAlchemy gives us changed version
        val = self.db.get_condition(1, ct)
        self.assertEqual(val.value, 30)

        # Roll back changes
        self.db.session.rollback()
        val = self.db.get_condition(1, ct)
        self.assertEqual(val.value, 10)

















