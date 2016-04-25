import inspect
import os
from datetime import datetime
import test_get_runs
import unittest
from rcdb.config_parser import parse_file, ConfigFileParseResult


class TestCodaParser(unittest.TestCase):
    """ Tests ConditionType, ConditionValue classes and their operations in provider"""

    def setUp(self):
        self.this_dir = os.path.dirname(inspect.getfile(test_get_runs))
        self.this_dir = os.path.normpath(self.this_dir)
        self.section_names = ["TRIGGER", "GLOBAL","FCAL","BCAL","TOF","ST","TAGH","TAGM","PS","PSC","TPOL","CDC", "FDC"]

    def test_parse_intermediate_file(self):
        """Test of create_condition_type function"""

        # Create condition type
        result = parse_file(os.path.join(self.this_dir, "run-5627_FCAL_BCAL_PS_m7.conf"), self.section_names)

        self.assertItemsEqual(result.found_section_names, self.section_names)
        self.assertEqual(result.sections["TRIGGER"].entities["BUFFERLEVEL"], '1')


