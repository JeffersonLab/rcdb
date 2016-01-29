import inspect
import os
import unittest

import rcdb
import rcdb.model
import test_run

from rcdb.model import Run, ConfigurationFile


class TestRun(unittest.TestCase):
    """ Tests ConditionType, ConditionValue classes and their operations in provider"""

    def setUp(self):
        self.db = rcdb.ConfigurationProvider("sqlite://")
        rcdb.model.Base.metadata.create_all(self.db.engine)
        # create run
        self.db.create_run(1)
        self.db.create_run(2)
        self.this_dir = os.path.dirname(inspect.getfile(test_run))
        self.this_dir = os.path.normpath(self.this_dir)

    def tearDown(self):
        self.db.disconnect()

    def test_add_file(self):
        """Test of Run in db function"""
        path_4433 = os.path.join(self.this_dir, "4433_run.log")
        self.db.add_configuration_file(1, path_4433)
        self.db.add_configuration_file(2, path_4433)
        self.db.add_configuration_file(2, path_4433, content="123123")
        run_2 = self.db.get_run(2)
        query = self.db.session.query(ConfigurationFile)\
                    .filter(ConfigurationFile.runs.contains(run_2))\
                    .filter(ConfigurationFile.path == path_4433)
        self.assertEqual(query.count(), 2)


    def test_file_overwrite(self):
        """Test, how one file can be overwritten"""
        run = self.db.create_run(3)

        self.db.add_configuration_file(3, '/some/path', content='one', overwrite=True)
        self.db.add_configuration_file(3, '/some/path', content='two', overwrite=True)

        # count that we have only one file
        query = self.db.session.query(ConfigurationFile)\
                    .filter(ConfigurationFile.runs.contains(run))\
                    .filter(ConfigurationFile.path == '/some/path')
        self.assertEqual(query.count(), 1)

        conf_file = query.first()
        self.assertEqual(conf_file.content, 'two')



