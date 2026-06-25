import unittest
import os
import tempfile
from click.testing import CliRunner
from rcdb.cli.app import rcdb_cli
from rcdb.provider import RCDBProvider
from rcdb.provider import destroy_all_create_schema
from rcdb.model import RunPeriod


class TestCliFile(unittest.TestCase):
    """Tests for the `rcdb file ...` command group (vers, cat, runs, ls, search)."""

    def setUp(self):
        # Create a named temporary file for SQLite
        tmp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_file_name = tmp_file.name
        tmp_file.close()  # we only need the name

        self.connection_str = "sqlite:///" + self.db_file_name
        self.db = RCDBProvider(self.connection_str, check_version=False)
        destroy_all_create_schema(self.db)

        # ----------------------------------------------------------------
        # Seed two files with several versions across runs:
        #
        #   /conf/main.conf
        #       version "v1"  -> runs 100, 101
        #       version "v2"  -> runs 102, 103   (last run = 103)
        #   /conf/other.conf
        #       version "x1"  -> run  100
        # ----------------------------------------------------------------
        self.main_path = "/conf/main.conf"
        self.other_path = "/conf/other.conf"

        for run in (100, 101):
            self.db.add_configuration_file(run, self.main_path, content="v1 content")
        for run in (102, 103):
            self.db.add_configuration_file(run, self.main_path, content="v2 content CHANGED")
        self.db.add_configuration_file(100, self.other_path, content="x1 content")

        # Two files that differ only where a '_' / '%' sits, used to verify LIKE
        # wildcards in the search pattern are escaped (matched literally).
        self.underscore_path = "/conf/fadc250_example.conf"
        self.literal_path = "/conf/fadc250Xexample.conf"
        self.db.add_configuration_file(100, self.underscore_path, content="u")
        self.db.add_configuration_file(100, self.literal_path, content="l")

        # A run period whose name contains '-' to exercise positional ls parsing.
        self.period_name = "RunPeriod-2025-test"
        self.db.session.add(RunPeriod(name=self.period_name, run_min=102, run_max=103))
        self.db.session.commit()

        self.db.disconnect()  # release the file lock; tests reconnect via the CLI

    def tearDown(self):
        self.db.disconnect()
        if os.path.exists(self.db_file_name):
            try:
                os.remove(self.db_file_name)
            except OSError:
                pass

    def _run(self, *args):
        runner = CliRunner()
        return runner.invoke(rcdb_cli, ["--connection", self.connection_str, "file", *args])

    # ------------------------------------------------------------------
    # vers
    # ------------------------------------------------------------------
    def test_vers_lists_versions_with_last_run(self):
        result = self._run("vers", self.main_path)
        self.assertEqual(result.exit_code, 0, msg=result.output)
        lines = [ln for ln in result.output.splitlines() if ln.strip()]
        # Two distinct versions
        self.assertEqual(len(lines), 2, msg=result.output)
        # Default sort is by last run descending -> the v2 version (last run 103) first
        self.assertTrue(lines[0].endswith("- 103"), msg=result.output)
        self.assertTrue(lines[1].endswith("- 101"), msg=result.output)
        # Each row is "<hash> - <run>"
        for line in lines:
            self.assertIn(" - ", line)

    def test_vers_missing_file_errors(self):
        result = self._run("vers", "/does/not/exist")
        self.assertNotEqual(result.exit_code, 0)

    # ------------------------------------------------------------------
    # cat
    # ------------------------------------------------------------------
    def test_cat_by_positional_run(self):
        result = self._run("cat", self.main_path, "100")
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn("v1 content", result.output)
        self.assertNotIn("CHANGED", result.output)

    def test_cat_by_run_option(self):
        result = self._run("cat", self.main_path, "--run=103")
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn("v2 content CHANGED", result.output)

    def test_cat_by_hash_prefix(self):
        # Discover a version hash via `vers`, then cat by a short prefix of it.
        vers = self._run("vers", self.main_path)
        first_hash = vers.output.splitlines()[0].split(" - ")[0]
        prefix = first_hash[:8]

        result = self._run("cat", self.main_path, "--hash=" + prefix)
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn("v2 content CHANGED", result.output)

    def test_cat_no_selector_errors(self):
        result = self._run("cat", self.main_path)
        self.assertNotEqual(result.exit_code, 0)

    def test_cat_run_and_hash_conflict_errors(self):
        result = self._run("cat", self.main_path, "100", "--hash=abc")
        self.assertNotEqual(result.exit_code, 0)

    def test_cat_missing_run_errors_cleanly(self):
        result = self._run("cat", self.main_path, "999")
        self.assertNotEqual(result.exit_code, 0)
        self.assertNotIn("Traceback", result.output)

    # ------------------------------------------------------------------
    # runs
    # ------------------------------------------------------------------
    def test_runs_default_desc(self):
        result = self._run("runs", self.main_path)
        self.assertEqual(result.exit_code, 0, msg=result.output)
        run_numbers = [int(ln.split(" - ")[0]) for ln in result.output.splitlines() if ln.strip()]
        self.assertEqual(run_numbers, [103, 102, 101, 100], msg=result.output)

    def test_runs_asc_and_limit(self):
        result = self._run("runs", self.main_path, "--asc", "--limit=2")
        self.assertEqual(result.exit_code, 0, msg=result.output)
        run_numbers = [int(ln.split(" - ")[0]) for ln in result.output.splitlines() if ln.strip()]
        self.assertEqual(run_numbers, [100, 101], msg=result.output)

    def test_runs_with_range(self):
        result = self._run("runs", self.main_path, "--run-min=101", "--run-max=102")
        self.assertEqual(result.exit_code, 0, msg=result.output)
        run_numbers = sorted(int(ln.split(" - ")[0]) for ln in result.output.splitlines() if ln.strip())
        self.assertEqual(run_numbers, [101, 102], msg=result.output)

    def test_runs_single_run(self):
        result = self._run("runs", self.main_path, "--run=100")
        self.assertEqual(result.exit_code, 0, msg=result.output)
        run_numbers = [int(ln.split(" - ")[0]) for ln in result.output.splitlines() if ln.strip()]
        self.assertEqual(run_numbers, [100], msg=result.output)

    def test_runs_mutually_exclusive_filters_error(self):
        result = self._run("runs", self.main_path, "--run=100", "--run-min=50")
        self.assertNotEqual(result.exit_code, 0)

    # ------------------------------------------------------------------
    # ls
    # ------------------------------------------------------------------
    def test_ls_all(self):
        result = self._run("ls")
        self.assertEqual(result.exit_code, 0, msg=result.output)
        # Both files appear, sorted by name (main before other)
        paths = [ln.split(" - ", 1)[1] for ln in result.output.splitlines() if " - " in ln]
        self.assertIn(self.main_path, paths)
        self.assertIn(self.other_path, paths)
        self.assertEqual(paths, sorted(paths), msg=result.output)

    def test_ls_single_run(self):
        # Run 103 only has the v2 version of main.conf, not other.conf
        result = self._run("ls", "--run=103")
        self.assertEqual(result.exit_code, 0, msg=result.output)
        paths = [ln.split(" - ", 1)[1] for ln in result.output.splitlines() if " - " in ln]
        self.assertEqual(paths, [self.main_path], msg=result.output)

    def _ls_paths(self, *args):
        result = self._run("ls", *args)
        self.assertEqual(result.exit_code, 0, msg=result.output)
        return [ln.split(" - ", 1)[1] for ln in result.output.splitlines() if " - " in ln]

    def test_ls_positional_single_run(self):
        # `ls 103` is treated as `ls --run=103`
        self.assertEqual(self._ls_paths("103"), [self.main_path])

    def test_ls_positional_run_range(self):
        # `ls 102-103` is treated as a run range; only main.conf spans it
        self.assertEqual(self._ls_paths("102-103"), [self.main_path])

    def test_ls_positional_open_range(self):
        # `ls 101-` means run 101 to the end. Runs 101-103 cover both versions
        # of main.conf (v1 on 101, v2 on 102-103), so both rows are main.conf.
        paths = self._ls_paths("101-")
        self.assertEqual(set(paths), {self.main_path}, msg=paths)
        self.assertNotIn(self.other_path, paths)

    def test_ls_positional_run_period_name(self):
        # `ls <period name>` resolves the period range (102-103 here). The name
        # itself contains '-' and must not be parsed as a numeric range.
        self.assertEqual(self._ls_paths(self.period_name), [self.main_path])

    def test_ls_positional_unknown_name_errors(self):
        result = self._run("ls", "NoSuchPeriod")
        self.assertNotEqual(result.exit_code, 0)

    def test_ls_positional_and_option_conflict_errors(self):
        result = self._run("ls", "100", "--run=100")
        self.assertNotEqual(result.exit_code, 0)

    # ------------------------------------------------------------------
    # search
    # ------------------------------------------------------------------
    def test_search_substring(self):
        result = self._run("search", "main")
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn(self.main_path, result.output)
        self.assertNotIn(self.other_path, result.output)

    def test_search_common_substring_matches_all(self):
        result = self._run("search", "conf")
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn(self.main_path, result.output)
        self.assertIn(self.other_path, result.output)

    def test_search_underscore_is_literal(self):
        # The '_' must be matched literally, not as a LIKE single-char wildcard,
        # so it must not also match "/conf/fadc250Xexample.conf".
        result = self._run("search", "fadc250_example")
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn(self.underscore_path, result.output)
        self.assertNotIn(self.literal_path, result.output)

    def test_search_is_case_insensitive(self):
        # Stored path is "/conf/main.conf" (lower case); an upper-case pattern
        # must still match.
        result = self._run("search", "MAIN")
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn(self.main_path, result.output)
        self.assertNotIn(self.other_path, result.output)


if __name__ == "__main__":
    unittest.main()
