import inspect
import os
from datetime import datetime
import test_run
import unittest
from rcdb.halld_daq_config_parser import parse_file, CodaRunLogParseResult


class TestDaqConfigParser(unittest.TestCase):
    """ Tests TestDaqConfigParser classes and their operations in provider"""

    def setUp(self):
        self.this_dir = os.path.dirname(inspect.getfile(test_run))
        self.this_dir = os.path.normpath(self.this_dir)

    def test_parse_daq_config_file(self):
        """Test of create_condition_type function"""

        # Create condition type
        result = parse_file(os.path.join(self.this_dir, "run-5627_FCAL_BCAL_PS_m7.conf"))

        self.assertIsInstance(result, CodaRunLogParseResult)
        self.assertIn('TRIGGER', result.section_names)
        self.assertTrue(len(result.trigger_equation), 6)
        self.assertEqual(result.trigger_equation[0], ['PS', '35', '10', '1'])
        self.assertEqual(len(result.trigger_type), 9)
        self.assertEqual(result.trigger_type[0], ['PS', '440', '5', '1300', '1900', '1100', '0', '3'])


