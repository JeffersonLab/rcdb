import unittest
import os
import tempfile
from click.testing import CliRunner
import rcdb
from rcdb.cli.app import rcdb_cli
from rcdb.provider import RCDBProvider
from rcdb.model import ConfigurationFile
from rcdb.provider import destroy_all_create_schema


class TestAddFile(unittest.TestCase):
    def setUp(self):
        # Create a named temporary file for SQLite
        tmp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_file_name = tmp_file.name
        tmp_file.close()   # we only need the name

        self.connection_str = "sqlite:///" + self.db_file_name
        self.db = RCDBProvider(self.connection_str, check_version=False)
        destroy_all_create_schema(self.db)
        self.db.disconnect()    # To remove lock from file

    def tearDown(self):
        self.db.disconnect()  # Should be no harm. Just in case
        if os.path.exists(self.db_file_name):
            try:
                os.remove(self.db_file_name)   # Try deleting file
            except:
                pass  # Do nothing

    def test_add_file_from_disk(self):
        """
        Test adding a file from the local filesystem to run #20
        """
        # Create a temporary file with some content
        fd, path = tempfile.mkstemp(prefix="rcdb_test_", suffix=".log")
        with open(path, "w") as f:
            f.write("Fake coda log content for run #20")

        runner = CliRunner()
        result = runner.invoke(rcdb_cli, [
            "--connection", self.connection_str,
            "add", "file", "20", path, "--importance", "2"
        ])
        self.assertEqual(result.exit_code, 0, msg=result.output)

        # Verify run #20
        run_20 = self.db.get_run(20)
        self.assertIsNotNone(run_20)

        # Verify the file got attached
        config_file = self.db.session.query(ConfigurationFile).filter(ConfigurationFile.path == path).one_or_none()
        self.assertIsNotNone(config_file)
        self.assertIn(run_20, config_file.runs)
        self.assertEqual(config_file.importance, 2)

        # Clean up
        os.close(fd)
        os.remove(path)

    def test_add_file_with_content_flag(self):
        """
        Test using the --content flag to store raw data without reading the file.
        """
        runner = CliRunner()
        result = runner.invoke(rcdb_cli, [
            "--connection", self.connection_str,
            "add", "file", "30", "/fake/path.log",  # file path that doesn't exist
            "--content", "HelloWorld123"
        ])
        self.assertEqual(result.exit_code, 0, msg=result.output)

        run_30 = self.db.get_run(30)
        self.assertIsNotNone(run_30)

        config_file = self.db.session.query(ConfigurationFile).filter(ConfigurationFile.path == "/fake/path.log").one()
        self.assertIsNotNone(config_file)
        self.assertIn(run_30, config_file.runs)
        self.assertIn("HelloWorld123", config_file.content)

    def test_overwrite_existing_file(self):
        """
        Test the --overwrite option that updates the content if the same path is re-added.
        """
        run = self.db.create_run(1)
        path = "/my/config.txt"

        # Add a file initially
        self.db.add_configuration_file(run, path, content="Original content", importance=0)

        # Now do it via CLI with --overwrite, new content
        runner = CliRunner()
        result = runner.invoke(rcdb_cli, [
            "--connection", self.connection_str,
            "add", "file", "1", path,
            "--overwrite",
            "--content", "Overwritten content"
        ])
        self.assertEqual(result.exit_code, 0, msg=result.output)

        # Check it
        cfg_file = self.db.session.query(ConfigurationFile).filter(ConfigurationFile.path == path).one()
        self.assertIn("Overwritten content", cfg_file.content)
        self.assertNotIn("Original content", cfg_file.content)
