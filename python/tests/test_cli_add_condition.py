import os
import tempfile
import unittest
from click.testing import CliRunner

from rcdb.cli.app import rcdb_cli
from rcdb.provider import RCDBProvider, destroy_all_create_schema
from rcdb.model import ConditionType


class TestAddCondition(unittest.TestCase):
    def setUp(self):
        """
        Creates a temporary SQLite file and initializes a fresh RCDB schema.
        Then we disconnect so the file is not locked on Windows.
        """
        tmp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_file_name = tmp_file.name
        tmp_file.close()  # we only need the path

        self.connection_str = "sqlite:///" + self.db_file_name

        # Create the schema
        self.db = RCDBProvider(self.connection_str, check_version=False)
        destroy_all_create_schema(self.db)
        self.db.session.commit()  # Important: commit the new schema
        self.db.disconnect()

    def tearDown(self):
        """
        Disconnect if needed and remove the temporary .db file
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

    def test_add_condition_new_run(self):
        """
        Test adding a condition to a run that doesn't exist yet
        => should create run #10 automatically.
        """
        # Reconnect, create the "beam_current" condition type, commit, then disconnect
        self.db = RCDBProvider(self.connection_str, check_version=False)
        self.db.create_condition_type("beam_current", ConditionType.FLOAT_FIELD, "Beam current")
        self.db.session.commit()
        self.db.disconnect()

        runner = CliRunner()
        result = runner.invoke(rcdb_cli, [
            "--connection", self.connection_str,
            "add", "condition", "10", "beam_current", "123.4"
        ])

        print("Output:\n", result.output)
        if result.exception:
            print("Exception:", result.exception)

        self.assertEqual(result.exit_code, 0, msg=result.output)

        # Check DB by reconnecting
        self.db = RCDBProvider(self.connection_str, check_version=False)
        run_10 = self.db.get_run(10)
        self.assertIsNotNone(run_10, "Run #10 should be created automatically by 'add condition'")
        val = run_10.get_condition_value("beam_current")
        self.assertEqual(float(val), 123.4)

    def test_add_condition_existing_run(self):
        """
        If run #5 exists, adding condition to it should just attach to the existing run.
        Must also create the 'is_production' condition type so the CLI won't error.
        """
        self.db = RCDBProvider(self.connection_str, check_version=False)
        # 1) Create run #5
        self.db.create_run(5)
        # 2) Also create 'is_production' condition type
        self.db.create_condition_type("is_production", ConditionType.BOOL_FIELD, "Production run?")
        self.db.session.commit()
        self.db.disconnect()

        runner = CliRunner()
        result = runner.invoke(rcdb_cli, [
            "--connection", self.connection_str,
            "add", "condition", "5", "is_production", "True"
        ])
        self.assertEqual(result.exit_code, 0, msg=result.output)

        # Check results
        self.db = RCDBProvider(self.connection_str, check_version=False)
        run_5 = self.db.get_run(5)
        self.assertIsNotNone(run_5)

        val = run_5.get_condition_value("is_production")
        self.assertEqual(val, True)

    def test_add_condition_replace(self):
        """
        If we already have a condition, test the --replace functionality
        to overwrite it with a new value.
        """
        self.db = RCDBProvider(self.connection_str, check_version=False)
        # Make sure the condition type exists
        self.db.create_condition_type("beam_current", ConditionType.FLOAT_FIELD, "Beam current")

        # Create run #1 and add beam_current=999.9
        self.db.create_run(1)
        self.db.add_condition(1, "beam_current", 999.9)
        self.db.session.commit()
        self.db.disconnect()

        runner = CliRunner()
        result = runner.invoke(rcdb_cli, [
            "--connection", self.connection_str,
            "add", "condition", "1", "beam_current", "100.1", "--replace"
        ])
        self.assertEqual(result.exit_code, 0, msg=result.output)

        # Check
        self.db = RCDBProvider(self.connection_str, check_version=False)
        run_1 = self.db.get_run(1)
        self.assertIsNotNone(run_1)
        self.assertEqual(float(run_1.get_condition_value("beam_current")), 100.1)

    def test_add_condition_missing_type(self):
        """
        If the condition type isn't in DB, the CLI should fail with an error.
        """
        runner = CliRunner()
        result = runner.invoke(rcdb_cli, [
            "--connection", self.connection_str,
            "add", "condition", "2", "non_existent_type", "X"
        ])
        self.assertNotEqual(result.exit_code, 0)  # Should fail
        self.assertIn("ERROR: No condition type 'non_existent_type' found", result.output)
