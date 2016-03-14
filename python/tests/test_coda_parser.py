import inspect
import os
from datetime import datetime
import test_run
import unittest
import rcdb
import rcdb.model
from rcdb.model import ConditionType, Condition, Run
from rcdb.coda_parser import parse_file

import logging

# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


class TestCodaParser(unittest.TestCase):
    """ Tests ConditionType, ConditionValue classes and their operations in provider"""

    def setUp(self):
        self.db = rcdb.ConfigurationProvider("sqlite://")
        rcdb.model.Base.metadata.create_all(self.db.engine)
        # create run
        self.this_dir = os.path.dirname(inspect.getfile(test_run))
        self.this_dir = os.path.normpath(self.this_dir)

    def tearDown(self):
        self.db.disconnect()

    def test_parse_intermediate_file(self):
        """Test of create_condition_type function"""

        # Create condition type
        run, run_config_file = parse_file(self.db, os.path.join(self.this_dir, "intermediate_update_run.log"))

        self.assertEqual(run.number, 10058)

        event_count = self.db.get_condition(run, rcdb.DefaultConditions.EVENT_COUNT)
        self.assertEqual(event_count.value, 293798)

