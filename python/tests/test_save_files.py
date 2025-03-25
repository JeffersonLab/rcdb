import os
import tempfile
import unittest

import rcdb
from rcdb.model import ConfigurationFile
from rcdb.provider import RCDBProvider, destroy_all_create_schema


class TestSaveFiles(unittest.TestCase):
    """
    Tests adding files to RCDB runs (ConfigurationFile attachments).
    Uses a temporary SQLite file-based DB for each test.
    """

    def setUp(self):
        """
        1) Creates a temp .db file so the test can share the same persistent schema/data.
        2) Creates and commits the schema, then leaves DB connected for the test.
        3) Sets self.this_dir so we can find local log files.
        """
        self.this_dir = os.path.dirname(__file__)

        tmp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_file_name = tmp_file.name
        tmp_file.close()  # We only needed the path

        self.connection_str = "sqlite:///" + self.db_file_name

        # Create RCDB schema in the SQLite file
        self.db = rcdb.ConfigurationProvider(self.connection_str, check_version=False)
        destroy_all_create_schema(self.db)
        self.db.session.commit()  # Ensure schema is persisted

    def tearDown(self):
        """
        1) Disconnects from the DB to release file locks (important on Windows).
        2) Removes the temp .db file after the test finishes.
        """
        try:
            self.db.disconnect()
        except:
            pass

        if os.path.exists(self.db_file_name):
            try:
                os.remove(self.db_file_name)
            except:
                pass

    def test_add_file(self):
        """
        Test adding a file to run #1 and run #2, then overwriting run #2's content.
        """
        path_4433 = os.path.join(self.this_dir, "4433_run.log")

        # By default, add_configuration_file() will create the run if it doesn't exist
        self.db.add_configuration_file(1, path_4433)
        self.db.add_configuration_file(2, path_4433)
        self.db.add_configuration_file(2, path_4433, content="123123")

        run_2 = self.db.get_run(2)
        query = self.db.session.query(ConfigurationFile) \
            .filter(ConfigurationFile.runs.contains(run_2)) \
            .filter(ConfigurationFile.path == path_4433)

        # We expect 2 separate ConfigurationFile rows: one for run #1, one for run #2
        self.assertEqual(query.count(), 2)

    def test_file_overwrite(self):
        """
        Test overwriting a file for run #3 so that only 1 ConfigurationFile row remains,
        but with updated content.
        """
        self.db.add_configuration_file(3, '/some/path', content='one', overwrite=True)
        self.db.add_configuration_file(3, '/some/path', content='two', overwrite=True)

        run_3 = self.db.get_run(3)
        query = self.db.session.query(ConfigurationFile) \
            .filter(ConfigurationFile.runs.contains(run_3)) \
            .filter(ConfigurationFile.path == '/some/path')

        # Only 1 row should remain (overwrite=True updates the same row)
        self.assertEqual(query.count(), 1)

        conf_file = query.first()
        self.assertEqual(conf_file.content, 'two')

    def test_large_file(self):
        """
        Test adding a 'large' log file with known content to run #1.
        Checks that the file content in DB includes '</coda>'.
        If the file doesn't exist, we skip the test.
        """
        path_large = os.path.join(self.this_dir, "large_run.log")

        if not os.path.exists(path_large):
            self.skipTest(f"File {path_large} not found, skipping 'large_run.log' test.")

        # Add the large file to run #1
        cf = self.db.add_configuration_file(1, path_large)
        content = self.db.session.query(ConfigurationFile.content).filter_by(id=cf.id).scalar()

        # Check if the known marker string is in the content
        self.assertIn("</coda>", content, "Expected '</coda>' inside large_run.log content")
