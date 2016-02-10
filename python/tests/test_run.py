import unittest

import rcdb
import rcdb.model
from rcdb.model import Run


class TestRun(unittest.TestCase):
    """ Tests ConditionType, ConditionValue classes and their operations in provider"""

    def setUp(self):
        self.db = rcdb.RCDBProvider("sqlite://")
        rcdb.model.Base.metadata.create_all(self.db.engine)
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
        run1 = self.db.create_run(1)
        run3 = self.db.create_run(3)
        run5 = self.db.create_run(5)

        runs = self.db.get_runs(0, 3)
        self.assertEqual(len(runs), 2)
        self.assertEqual(runs[0].number, 1)
        self.assertEqual(runs[1].number, 3)


