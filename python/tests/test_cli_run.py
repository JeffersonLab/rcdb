import unittest
import os
import datetime
import tempfile
from click.testing import CliRunner
from rcdb.cli.app import rcdb_cli
from rcdb.provider import RCDBProvider
from rcdb.provider import destroy_all_create_schema
from rcdb.model import ConditionType


class TestCliRun(unittest.TestCase):
    """Tests for the `rcdb run <number>` command (and the `rcdb <number>` shortcut)."""

    def setUp(self):
        tmp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_file_name = tmp_file.name
        tmp_file.close()

        self.connection_str = "sqlite:///" + self.db_file_name
        self.db = RCDBProvider(self.connection_str, check_version=False)
        destroy_all_create_schema(self.db)

        # Condition types
        self.db.create_condition_type("beam_current", ConditionType.FLOAT_FIELD, "")
        self.db.create_condition_type("comment", ConditionType.STRING_FIELD, "")

        # Run 1000 with a time span, two conditions and two files
        run = self.db.create_run(1000)
        self.db.add_run_start_time(run, datetime.datetime(2025, 3, 10, 11, 0, 0))
        self.db.add_run_end_time(run, datetime.datetime(2025, 3, 10, 12, 30, 0))

        self.db.add_condition(run, "beam_current", 12.5)
        # A multi-line, long string condition to exercise flatten + truncation
        self.long_comment = "line one\n" + ("x" * 80)
        self.db.add_condition(run, "comment", self.long_comment)

        self.db.add_configuration_file(run, "/conf/daq.conf", content="daq", importance=0)  # HIGH
        self.db.add_configuration_file(run, "/conf/notes.log", content="notes", importance=1)  # LOW

        self.db.session.commit()
        self.db.disconnect()

    def tearDown(self):
        self.db.disconnect()
        if os.path.exists(self.db_file_name):
            try:
                os.remove(self.db_file_name)
            except OSError:
                pass

    def _run(self, *args):
        runner = CliRunner()
        return runner.invoke(rcdb_cli, ["--connection", self.connection_str, *args])

    # ------------------------------------------------------------------
    # Full report
    # ------------------------------------------------------------------
    def test_full_report(self):
        result = self._run("run", "1000")
        self.assertEqual(result.exit_code, 0, msg=result.output)
        out = result.output
        # Info line with both times
        self.assertIn("Run 1000:", out)
        self.assertIn("2025-03-10 11:00:00", out)
        self.assertIn("2025-03-10 12:30:00", out)
        # Section titles
        self.assertIn("CONDITIONS:", out)
        self.assertIn("FILES", out)
        self.assertIn("important:", out)
        self.assertIn("other files:", out)
        # Conditions sorted by name -> beam_current before comment
        self.assertLess(out.index("beam_current"), out.index("comment"))
        # Files grouped by importance
        self.assertIn("/conf/daq.conf", out)
        self.assertIn("/conf/notes.log", out)
        self.assertLess(out.index("/conf/daq.conf"), out.index("/conf/notes.log"))

    def test_string_value_flattened_and_truncated(self):
        result = self._run("run", "1000", "-c")
        self.assertEqual(result.exit_code, 0, msg=result.output)
        out = result.output
        # No newline from the stored value should survive
        comment_line = [ln for ln in out.splitlines() if "comment" in ln][0]
        self.assertNotIn("\n", comment_line.replace("\n", ""))  # line itself is single
        # Truncated to 50 chars of value + "..."
        self.assertIn("...", comment_line)
        value_part = comment_line.split(" - ", 1)[1]
        self.assertEqual(len(value_part), 50 + len("..."))

    # ------------------------------------------------------------------
    # Selective flags
    # ------------------------------------------------------------------
    def test_info_only(self):
        result = self._run("run", "1000", "-i")
        self.assertEqual(result.exit_code, 0, msg=result.output)
        out = result.output
        self.assertIn("Run 1000:", out)
        self.assertNotIn("CONDITIONS:", out)
        self.assertNotIn("FILES", out)
        self.assertNotIn("beam_current", out)

    def test_conditions_only_no_title(self):
        result = self._run("run", "1000", "--conditions")
        self.assertEqual(result.exit_code, 0, msg=result.output)
        out = result.output
        self.assertNotIn("CONDITIONS:", out)
        self.assertNotIn("Run 1000:", out)
        self.assertNotIn("FILES", out)
        self.assertIn("beam_current - 12.5", out)

    def test_files_only_no_title(self):
        result = self._run("run", "1000", "-f")
        self.assertEqual(result.exit_code, 0, msg=result.output)
        out = result.output
        self.assertNotIn("FILES", out)
        self.assertNotIn("CONDITIONS:", out)
        self.assertNotIn("Run 1000:", out)
        # Importance grouping labels stay
        self.assertIn("important:", out)
        self.assertIn("/conf/daq.conf", out)
        self.assertIn("/conf/notes.log", out)

    def test_combined_flags(self):
        result = self._run("run", "1000", "-i", "-f")
        self.assertEqual(result.exit_code, 0, msg=result.output)
        out = result.output
        self.assertIn("Run 1000:", out)
        self.assertIn("/conf/daq.conf", out)
        self.assertNotIn("beam_current", out)  # conditions not requested

    # ------------------------------------------------------------------
    # Shortcut & errors
    # ------------------------------------------------------------------
    def test_number_shortcut_equals_run(self):
        shortcut = self._run("1000")
        explicit = self._run("run", "1000")
        self.assertEqual(shortcut.exit_code, 0, msg=shortcut.output)
        self.assertEqual(shortcut.output, explicit.output)

    def test_number_shortcut_with_flag(self):
        result = self._run("1000", "-c")
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn("beam_current - 12.5", result.output)
        self.assertNotIn("Run 1000:", result.output)

    def test_missing_run_errors_cleanly(self):
        result = self._run("run", "999")
        self.assertNotEqual(result.exit_code, 0)
        self.assertNotIn("Traceback", result.output)


if __name__ == "__main__":
    unittest.main()
