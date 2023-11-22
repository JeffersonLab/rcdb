import unittest

import rcdb
import rcdb.model
from rcdb.model import RunPeriod
import datetime

"""
Example of run periods table used in this unit tests:
Yet another data example is here: 
https://halldweb.jlab.org/wiki/index.php/Run_Periods

run_periods = {
    "2017-01": (30000, 39999, "23 Jan 2017 - 13 Mar 2017   12 GeV e-"),
    "2016-10": (20000, 29999, "15 Sep 2016 - 21 Dec 2016   12 GeV e-"),
    "2016-02": (10000, 19999, "28 Jan 2016 - 24 Apr 2016   Commissioning, 12 GeV e-"),
    "2015-12": (3939, 4807,   "01 Dec 2015 - 28 Jan 2016   Commissioning, 12 GeV e-, Cosmics"),
    "2015-06": (3386, 3938,   "29 May 2015 - 01 Dec 2015   Cosmics"),
    "2015-03": (2607, 3385,   "11 Mar 2015 - 29 May 2015   Commissioning, 5.5 GeV e-"),
    "2015-01": (2440, 2606,   "06 Feb 2015 - 11 Mar 2015   Cosmics"),
    "2014-10": (630, 2439,    "28 Oct 2014 - 21 Dec 2014   Commissioning, 10 GeV e-"),
}
"""

class TestRunPeriod(unittest.TestCase):
    def setUp(self):
        self.db = rcdb.RCDBProvider("sqlite://", check_version=False)
        rcdb.provider.destroy_all_create_schema(self.db)

    def tearDown(self):
        self.db.disconnect()

    def test_create_run_periods(self):
        """Test of Run in db function"""

        rp = self.db.create_run_period("Gluex 2017-01",
                                       "12 GeV e-",
                                       30000,
                                       39999,
                                       datetime.date(2017,1, 23),
                                       datetime.date(2017, 3, 13))
        self.assertEqual(rp.name, "Gluex 2017-01")
        self.assertEqual(rp.description, "12 GeV e-")
        self.assertEqual(rp.start_date, datetime.date(2017,1, 23))
        self.assertEqual(rp.end_date, datetime.date(2017, 3, 13))
        self.assertEqual(rp.run_min, 30000)
        self.assertEqual(rp.run_max, 39999)

    def test_get_run_periods(self):
        self.db.create_run_period("Gluex 2017-01",
                                  "12 GeV e-",
                                  30000,
                                  39999,
                                  datetime.date(2017,1, 23),
                                  datetime.date(2017, 3, 13))

        self.db.create_run_period("Gluex 2016-02",
                                  "End of GlueX phase",
                                  20000,
                                  29999,
                                  datetime.date(2016,9, 15),
                                  datetime.date(2016, 12, 21))
        rps = self.db.get_run_periods()
        self.assertEqual(len(rps), 2)


if __name__ == '__main__':
    unittest.main()
