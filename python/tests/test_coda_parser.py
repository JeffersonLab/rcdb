import inspect
import os
from datetime import datetime
import unittest

from rcdb.coda_parser import parse_file, CodaRunLogParseResult




class TestCodaParser(unittest.TestCase):
    """ Tests ConditionType, ConditionValue classes and their operations in provider"""

    def setUp(self):
        self.this_dir = os.path.dirname(inspect.getfile(test_get_runs))
        self.this_dir = os.path.normpath(self.this_dir)

    def test_parse_intermediate_file(self):
        """Test of create_condition_type function"""

        # Create condition type
        result = parse_file(os.path.join(self.this_dir, "intermediate_update_run.log"))

        awaited_start_time = datetime.strptime('02/01/16 19:25:32', "%m/%d/%y %H:%M:%S")
        awaited_update_time = datetime.strptime('02/01/16 19:56:50', "%m/%d/%y %H:%M:%S")

        self.assertIsInstance(result, CodaRunLogParseResult)

        self.assertEqual(result.run_number, 10058)

        self.assertEqual(result.has_run_start, True)                # File has <run-start> xml section
        self.assertEqual(result.has_run_end, False)                 # File has <run-end> xml section
        self.assertEqual(result.run_type, 'hd_bcal.tsg')            # the Run type. E.g. 'hd_all.tsg_cosmic'
        self.assertEqual(result.session, 'hdops')                   # Session E.g. 'hdops'
        self.assertEqual(result.start_time, awaited_start_time)     # Start time
        self.assertIsNone(result.end_time)                          # Time of the run end
        self.assertEqual(result.update_time, awaited_update_time)   # Time when the coda log file is written
        self.assertEqual(result.event_count, 293798)                # The number of events in the run
        self.assertTrue(result.components)                          # a list of names of <components> section
        self.assertIn('ROCBCAL10', result.components)
        self.assertTrue(result.component_stats)                     # dictionary with contents
        self.assertIn('ROCBCAL10', result.component_stats.keys())
        self.assertTrue(result.rtvs)                                # dictionary with contents of <rtvs> section
        self.assertIn('%(CODA_ROLMC)', result.rtvs.keys())

        # config file with full path.
        self.assertEqual(result.run_config_file, '/home/hdops/CDAQ/daq_dev_v0.31/daq/config/hd_bcal/bcal_phys_led.conf')
        self.assertEqual(result.run_config, 'bcal_phys_led.conf')        # config file name

    def test_parse_file_with_end_run(self):

        # Create condition type
        result = parse_file(os.path.join(self.this_dir, "large_run.log"))

        awaited_end_time = datetime.strptime('02/15/16 15:17:50', "%m/%d/%y %H:%M:%S")

        self.assertIsInstance(result, CodaRunLogParseResult)
        self.assertEqual(result.event_count, 10729318)
        self.assertEqual(result.has_run_end, True)
        self.assertEqual(result.end_time, awaited_end_time)
        self.assertIn('monitoring test', result.user_comment)

    def test_evio_files(self):
        result = parse_file(os.path.join(self.this_dir, "10340_run.log"))
        self.assertEqual(result.evio_files_count, 2)
        self.assertEqual(result.evio_last_file, "hd_rawdata_010340_001.evio")
