import unittest

import rcdb
import rcdb.model
from rcdb.model import ConditionType


class TestRun(unittest.TestCase):
    """ Tests ConditionType, ConditionValue classes and their operations in provider"""

    def setUp(self):
        self.db = rcdb.RCDBProvider("sqlite://", check_version=False)
        rcdb.provider.destroy_all_create_schema(self.db)
        # create run
        self.db.create_run(1)

    def tearDown(self):
        self.db.disconnect()

    def test_creating_run(self):
        """Test of Run in db function"""
        run = self.db.create_run(1)
        run2 = self.db.create_run(1)    # call it again. It should be the same object
        self.assertEqual(run, run2)
        self.assertEqual(run.number, 1)

    def test_get_next_prev_run(self):
        run1 = self.db.create_run(1)
        run3 = self.db.create_run(3)
        run5 = self.db.create_run(5)

        test_run = self.db.get_next_run(3)
        test_run2 = self.db.get_next_run(run3)

        self.assertEqual(test_run.number, run5.number)
        self.assertEqual(test_run, test_run2)

        test_prev_run = self.db.get_prev_run(3)
        test_prev_run2 = self.db.get_prev_run(run3)
        self.assertEqual(test_prev_run.number, run1.number)
        self.assertEqual(test_prev_run, test_prev_run2)

    def test_get_runs(self):
        self.db.create_run(1)
        self.db.create_run(3)
        self.db.create_run(5)

        runs = self.db.get_runs(0, 3)
        self.assertEqual(len(runs), 2)
        self.assertEqual(runs[0].number, 1)
        self.assertEqual(runs[1].number, 3)

    def test_get_run_fail_safe(self):
        run1 = self.db.create_run(1)
        
        test_run = self.db.get_run(run1)    # put ubject instead of a number
        
        self.assertEqual(run1, test_run)

        test_run = self.db.get_run("1")     # put string which accidentally
        self.assertEqual(run1, test_run)

        self.assertRaises(ValueError, self.db.get_run, "foo")

    def test_get_conditions_from_run(self):

        # Create run, condition type and condition
        run1 = self.db.create_run(1)
        run2 = self.db.create_run(2)
        ct = self.db.create_condition_type("ct", ConditionType.STRING_FIELD, "Some condition type")
        self.db.add_condition(run1, ct, "haha")
        self.assertEqual(run2.number, 2)

        run1 = self.db.get_run(1)
        run2 = self.db.get_run(2)
        self.assertEqual(run1.get_condition_value("ct"), "haha")
        self.assertIsNone(run2.get_condition_value("ct"))
