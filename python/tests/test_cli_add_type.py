import os
import tempfile
import unittest
from click.testing import CliRunner
import rcdb
from rcdb.cli.app import rcdb_cli
from rcdb.provider import RCDBProvider
from rcdb.model import ConditionType
from rcdb.provider import destroy_all_create_schema


class TestAddType(unittest.TestCase):
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

    def test_add_type_float(self):
        """
        Test creating a new condition type (default float) via the CLI
        """
        runner = CliRunner()
        # Invoke the CLI with 'rcdb add type <name>'
        result = runner.invoke(rcdb_cli, [
            "--connection", self.connection_str,
            "add", "type", "my_test_cond"
            # No --type or --description => defaults to float, description=""
        ])

        self.assertEqual(result.exit_code, 0, msg=result.output)

        # Check that the condition type got created
        ct = self.db.get_condition_type("my_test_cond")
        self.assertIsNotNone(ct)
        self.assertEqual(ct.name, "my_test_cond")
        self.assertEqual(ct.value_type, ConditionType.FLOAT_FIELD)
        self.assertEqual(ct.description, "")

    def test_add_type_string_with_description(self):
        """
        Test creating a string condition type with a description
        """
        runner = CliRunner()
        result = runner.invoke(rcdb_cli, [
            "--connection", self.connection_str,
            "add", "type", "title",
            "--type", "string",
            "--description", "Some description"
        ])

        self.assertEqual(result.exit_code, 0, msg=result.output)

        # Check DB
        ct = self.db.get_condition_type("title")
        self.assertIsNotNone(ct)
        self.assertEqual(ct.value_type, ConditionType.STRING_FIELD)
        self.assertEqual(ct.description, "Some description")

    def test_add_type_bool(self):
        """
        Test creating a bool type
        """
        runner = CliRunner()
        result = runner.invoke(rcdb_cli, [
            "--connection", self.connection_str,
            "add", "type", "is_valid",
            "--type", "bool"
        ])
        self.assertEqual(result.exit_code, 0, msg=result.output)

        ct = self.db.get_condition_type("is_valid")
        self.assertIsNotNone(ct)
        self.assertEqual(ct.value_type, ConditionType.BOOL_FIELD)
