import unittest

import rcdb
import rcdb.model
from rcdb.model import RunPeriod


class TestRunPeriod(unittest.TestCase):
    def setUp(self):
        self.db = rcdb.RCDBProvider("sqlite://", check_version=False)
        rcdb.provider.destroy_all_create_schema(self.db)


    def tearDown(self):
        self.db.disconnect()


if __name__ == '__main__':
    unittest.main()
