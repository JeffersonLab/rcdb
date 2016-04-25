import inspect
import os
import unittest

import rcdb
import rcdb.model
import test_run

from rcdb.model import Run, ConfigurationFile


class TestSaveFiles(unittest.TestCase):
    """ Tests ConditionType, ConditionValue classes and their operations in provider"""

    @unittest.skip("rework of how coda files are parsed")
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

    @unittest.skip("rework of how coda files are parsed")
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

    @unittest.skip("rework of how coda files are parsed")
    def test_large_file(self):
        self.db = rcdb.ConfigurationProvider("mysql://rcdb@127.0.0.1/rcdb")

        path_4433 = os.path.join(self.this_dir, "large_run.log")
        cf = self.db.add_configuration_file(1, path_4433)
        content = self.db.session.query(ConfigurationFile.content).filter(ConfigurationFile.id == cf.id).scalar()
        self.assertIn("</coda>", content)



