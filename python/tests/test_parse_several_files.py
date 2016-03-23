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
import helpers


class TestParseSeveralFiles(unittest.TestCase):
    """ Tests ConditionType, ConditionValue classes and their operations in provider"""

    def setUp(self):
        self.db = helpers.create_memory_sqlite()
        # create run
        self.this_dir = os.path.dirname(inspect.getfile(test_run))
        self.this_dir = os.path.normpath(self.this_dir)

    def tearDown(self):
        self.db.disconnect()

    def tearDown(self):
        self.db.disconnect()

    @unittest.skip("rework of how coda files are parsed")
    def test_parse_intermediate_file(self):
        """Test of create_condition_type function"""

        # Create condition type
        run, run_config_file = parse_file(self.db, os.path.join(self.this_dir, "10340_run.log"))

        self.assertEqual(run.number, 10340)

    @unittest.skip("rework of how coda files are parsed")
    def test_parse_intermediate_file(self):
        """Test of create_condition_type function"""

        # Create condition type
        run, run_config_file = parse_file(self.db, os.path.join(self.this_dir, "large_run.log"))

        self.assertEqual(run.number, 10292)
        self.assertTrue(run.get_condition_value("is_valid_run_end"))
