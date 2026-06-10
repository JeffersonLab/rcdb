# RCDB Documentation Audit Report

## Executive Summary

29 documentation files were audited across the RCDB repository. No files are fully up-to-date and free of any issues. The overall health of the documentation is poor: the majority of files contain concrete API errors, Python 2 syntax in code examples, wrong method names, missing required arguments, and stale CLI command references.

**Status breakdown:**

| Status | Count | Files |
|---|---|---|
| needs-update | 17 | Adding-condition-values.md, concepts/connection.md, Cpp.md, development/development.md, development/documentation.md, development/rcdb2-migration.md, get-started/add-value-python.md, get-started/python.md, get-started/query-syntax.md, get-started/select-values.md, index.md, Java.md, python.md, rcdb-cli.md, Search-queries.md, Select-runs-and-get-values.md, SQLAlchemy.md, website/index.md, website/quick-query.md |
| minor-fixes | 8 | concepts/db-and-api-structure.md, Creating-condition-types.md, daq/daq.md, Database-Installation.md, get-started/installation.md, Logging.md, _sidebar.md, website/database-selector.md, website/install.md |
| obsolete | 1 | DaqConfigParser.md |
| current | 0 | — |

**Cross-cutting problems appearing in many files:**

- Python 2 bare `print` syntax used as runnable examples in at least 7 files (the project requires Python >=3.9)
- The `rcdb select` subcommand is documented in at least 4 files but is not registered in `cli/app.py`
- `ConfigurationProvider` is marked obsolete in source but still promoted in docs
- `create_condition_type(name, value_type, description)` has `description` documented as optional in multiple files; it is required

---

## Files Requiring Major Updates (needs-update)

### `docs/Adding-condition-values.md`

**Status:** needs-update

- **Wrong parameter name:** The doc declares `def add_conditions(run, name_values, replace=False)` and uses `name_values` throughout. The actual signature in `python/rcdb/provider.py:501` is `def add_conditions(self, run, key_values, replace=False)`. The parameter is named `key_values`, not `name_values`.
- **Missing required argument:** Multiple code examples call `db.create_condition_type("list_data", ConditionType.JSON_FIELD)` with only two arguments. The actual method signature (`provider.py:432`) requires three arguments: `name, value_type, description`. Omitting `description` raises `TypeError`.
- **Python 2 syntax:** Multiple code blocks use bare `print` statements: `print condition.value` (lines 86-95), `print restored_list`, `print restored_dict` (lines 168-173), `print "How cat is stored in DB:"` (lines 243-246). The package requires Python 3.9+.
- **Non-existent file paths:** References `$RCDB_HOME/python/example_conditions_store_array.py` and `$RCDB_HOME/python/create_empty_sqlite.py` (lines 190-197). Neither file exists. The actual equivalent is `python/examples/11_crete_conditions_store_array.py`.
- **Broken code fence:** The JSON_FIELD example code block at line 145 is never properly closed. Line 174 reads the bare word `python` instead of a closing triple-backtick, corrupting the Markdown rendering of all subsequent content.
- **Python 2 documentation link:** Line 128 links to `https://docs.python.org/2/library/json.html`. Lines 199-206 discuss `u"x"` unicode string notation, a Python 2 artefact. In Python 3 all strings are unicode; the section is misleading.
- **Minor:** The `jsonpickle` installation section (lines 262-275) only mentions `pip install`; the project uses `uv` as its package manager.

---

### `docs/concepts/connection.md`

**Status:** needs-update

- **Critical typo in env var name:** Line 45 shows `CCDB_CONNECTION` but the actual environment variable is `RCDB_CONNECTION`. Confirmed in `python/rcdb/cli/app.py:30`. CCDB is a completely different database project.
- **Incomplete CLI example:** Lines 49-50 show `rcdb -c  ` with no value following the flag, making the example non-functional.
- **Python 2 syntax:** Line 74: `print "connected to:", db.connection_string` must be `print("connected to:", db.connection_string)`.
- **Wrong C++ variable name:** Lines 93-94 use `prov.GetCondition(10173, "event_count")` but the actual example at `cpp/examples/simple.cpp` declares the connection as `rcdb::Connection connection(connection_str)` and calls `connection.GetCondition(...)`. The variable name `prov` does not appear anywhere in the C++ codebase.

---

### `docs/Cpp.md`

**Status:** needs-update

- **Wrong variable name in code snippet:** Line 99 shows `auto cnd = prov.GetCondition(10173, "event_count");` but the Connection object declared on line 96 is named `con`. The variable `prov` is never defined in the snippet; the example will not compile.
- **Wrong class name:** The `write_conditions.cpp` bullet (line 160) says "Using `WriteConnection`" but the actual class in `cpp/include/RCDB/WritingConnection.h` is `WritingConnection`. The example source `cpp/examples/write_conditions.cpp:8` uses `rcdb::WritingConnection`.
- **Wrong output directory claim:** The doc states examples are built to `$RCDB_HOME/cpp/bin` named as `exmpl_<...>`. The `cpp/CMakeLists.txt` has no `CMAKE_RUNTIME_OUTPUT_DIRECTORY`, no output renaming, and no install step. CMake places outputs in `cpp/build/` with names like `examples_trigger_params`. The `cpp/bin/` directory holds pre-built binaries unrelated to the documented `cmake --build build` workflow.
- **False CMake target claim:** `simple.cpp` (`cpp/examples/simple.cpp`) has no `add_executable` target in `cpp/CMakeLists.txt`. The doc implies it is built by `cmake --build build`, which is false.
- **Undocumented deprecation:** The API table (line 119) lists `rapidjson::Document ToJsonDocument()` without noting it is marked `/// @deprecated use json ToJson() instead` in `cpp/include/RCDB/Condition.h:86`.
- **Missing examples:** Three examples with CMake targets are absent from the "List of examples": `get_fadc_masks.cpp` (`examples_fadc_masks`), `write_array_to_json.cpp` (`examples_write_array_to_json`), `write_objects_to_json.cpp` (`examples_write_objects_to_json`).
- **Minor typo:** Line 47: "There is at lease C++11 support" — "lease" should be "least".

---

### `docs/development/development.md`

**Status:** needs-update

- **Broken relative link:** Line 37: `[Database Selector](development/database-selector.md)` — the file does not exist at `docs/development/database-selector.md`. The actual file is at `docs/website/database-selector.md`.
- **Non-existent environment variable:** Line 61 lists `CPLUS_INCLUDE_PATH` as set by the environment scripts, but none of the environment scripts (`environment.bash`, `environment.fish`, `environment.csh`, `environment.zsh`) set `CPLUS_INCLUDE_PATH`. No occurrence exists anywhere in the repo except this doc.
- **Missing env var entries:** The "Setup environment manually" section (lines 54-62) omits `PYTHONPATH` (set to `$RCDB_HOME/python` in all environment scripts) and `$RCDB_HOME/cpp/bin` from `PATH` (present in `environment.bash`).
- **Minor:** The "Publishing on pypi" section (lines 41-45) uses `python -m pip install build twine` and `python -m build`, inconsistent with the project's `uv` toolchain. The `uv` equivalents are `uv build` and `uv run twine upload dist/*`.

---

### `docs/development/documentation.md`

**Status:** needs-update

- **False claim about Doxygen:** Line 7 states "The C++ reference part is generated by Doxygen", but the `documentation.yml` workflow contains no Doxygen step. No `Doxyfile` exists anywhere in the repository. The C++ API documentation (`docs/Cpp.md`) is hand-written Markdown.
- **Stale coverpage claim:** Line 60 says `_coverpage.md is responsible for the cover page content (with gnomes as of 2024)`. The file `_coverpage.md` does not exist in `docs/`, and `docs/index.html` explicitly sets `coverpage: false`.
- **Typo:** Line 16: "Git Flawored Markdown" should be "Git Flavored Markdown".
- **Typo and bad link:** Line 85: "Docsify themebable" — "themebable" should be "themeable". The link also points to the demo site rather than the GitHub repository.
- **Broken link:** Line 86: `- Theme switcher [github](https://github.com/` — the URL is truncated and the link is broken/incomplete.

---

### `docs/development/rcdb2-migration.md`

**Status:** needs-update

- **Unregistered CLI command:** The doc presents `rcdb select ...` as a valid command (lines 28 and 77). The file `python/rcdb/cli/select.py` exists but the command is never added to the CLI app in `python/rcdb/cli/app.py`. Running `rcdb --help` confirms `select` is absent. Available subcommands are: `add, db, info, ls, repair, rp, web`.
- **Wrong table name:** Line 18 states the new table is named `alias` (singular). The actual table in `model.py:434` is `aliases` (plural), and the SQL migration file `sql/update_db_v1_to_v2.sql:12` creates table `aliases`.
- **Outdated Python version:** Line 82 says "Make sure you have Python 3.9+ (or 3.8 if tested)". `pyproject.toml` specifies `requires-python = ">=3.9"` with no mention of 3.8, which reached end-of-life in October 2024.
- **Minor:** The WSGI example path `/home/rcdb/rcdb_current/python` is a placeholder that is installation-specific but not labeled as such.

---

### `docs/get-started/add-value-python.md`

**Status:** needs-update

- **Promotes obsolete class:** Section 5 and the Complete Example recommend `ConfigurationProvider` for attaching files. `provider.py:1419-1420` marks it: "Obsolete. Still exists for backward compatibility. All methods moved to `RCDBProvider`." The doc's statement that "`ConfigurationProvider` is a subclass of `RCDBProvider` that adds handy methods for adding files" is no longer accurate — it is now an empty pass-through class.
- **Wrong import for `add_configuration_file`:** The import in section 5 and the Complete Example uses `ConfigurationProvider` specifically to call `add_configuration_file`, but that method is defined on `RCDBProvider` (`provider.py:758`), not `ConfigurationProvider`. The doc should import and use `RCDBProvider` instead.
- **Obsolete method undisclosed:** Section 6.2 lists `db.select_runs(...)` without noting it is marked obsolete. `provider.py:849` begins its docstring with "Obsolete. Searches RCDB...".
- **Minor:** No connection setup is shown before sections 2-4, which all call `db.create_condition_type / db.create_run / db.add_condition` without establishing `db`. The Complete Example fills this gap but earlier sections are left dangling.

---

### `docs/get-started/python.md`

**Status:** needs-update

- **Code example raises `NoRunFoundError` at runtime:** Lines 19-23 call `db.add_condition(run=1, ...)` without first calling `db.create_run(1)`. The actual `add_conditions()` implementation (`provider.py:534-540`) calls `self.get_run(run_number)` and raises `NoRunFoundError` if the run does not exist. The authoritative example `python/examples/10_create_conditions_basic.py:18` calls `db.create_run(1)` before any `add_condition` call.
- **Unused import:** Line 9: `from datetime import datetime` is imported but `datetime` is never used anywhere in the shown code block.
- **Non-existent file reference:** The "Running the Example" section (step 2, line 90) instructs readers to run `python example_conditions_basic.py`, but no file by that name exists in the repository. The closest actual file is `python/examples/10_create_conditions_basic.py`.

---

### `docs/get-started/query-syntax.md`

**Status:** needs-update

- **Wrong CLI command name and unregistered subcommand:** Line 26 shows `rcdb sel "..."` but the actual command name in `python/rcdb/cli/select.py:30` is `name="select"`. Furthermore, `select_command` is never imported or registered in `python/rcdb/cli/app.py` — it is absent entirely from `rcdb_cli.commands`. The CLI example would fail with "No such command 'sel'".
- **Python 2 documentation link:** Line 31 links to `https://docs.python.org/2/library/stdtypes.html`. The project requires Python >=3.9. The link should point to `https://docs.python.org/3/library/stdtypes.html`.
- **Inaccurate alias definition:** The `@is_production` alias shown (lines 58-64) omits the null-guard checks present in the actual source. `python/rcdb/alias.py:10,12` has `beam_current and beam_current > 2` and `solenoid_current and solenoid_current > 100`. The doc shows the expressions without the null guards, making them inaccurate and potentially misleading about NULL handling.

---

### `docs/get-started/select-values.md`

**Status:** needs-update

- **Wrong GitHub paths for example files:** Lines 38-40 link to `python/01_select_values_simple.py`, `python/02_select_value_extended.py`, `python/03_select_values_custom_runs.py`. The actual files live under `python/examples/` (e.g., `python/examples/01_select_values_simple.py`).
- **Filename typo:** The linked filename `02_select_value_extended.py` is misspelled — the real file is `02_select_values_extended.py` (missing the `s` in `values`).
- **Python 2 syntax:** Line 54: `print row[0], row[1], row[2]` must be `print(row[0], row[1], row[2])`.
- **Inconsistent database name:** The TLDR section connects to `rcdb2` (line 17), the "Select and filter" section uses `rcdb` (line 47), and the one-liner at line 151 also uses `rcdb`. The actual example files all use `rcdb2`.
- **Stale/misleading claim about CLI:** Line 154 states: "It was planned to have `rcdb sel` command doing it. But it hasn't been fully implemented yet." In reality, a full `select` CLI command is implemented at `python/rcdb/cli/select.py` but is simply not registered in `app.py`. The statement is misleading about the state of the code.
- **Minor:** Line 99: malformed backtick — triple-backtick open, double-backtick close; produces broken rendering.

---

### `docs/index.md`

**Status:** needs-update

- **Non-functional CLI example:** Line 55 shows `rcdb 1000 event_count` as a way to view a condition value. The current `rcdb` CLI is a Click group that requires a subcommand (`add, ls, info, rp, web, db, repair`). Bare positional arguments are not accepted.
- **Non-existent CLI flag:** Line 57: `rcnd --search "event_count > 500"` — the `--search` flag does not exist in `python/utilities/rcnd.py`. The defined flags are: `--write, --replace, --list, --create, --new-run, --type, --description, --list-names, -c/--connection, -v/--verbose`.
- **Misleading `rcnd --write` comment:** Line 56 shows `rcnd --write 1663 100 event_count` with the comment `# Write condition value to run 100`, which could confuse readers into thinking `1663` is a run number.
- **Unregistered `select` subcommand:** Line 56's implied intent of showing run search could be addressed by `rcdb select`, but that subcommand is not registered in `python/rcdb/cli/app.py:67`.
- **Minor:** Line 10: "Possibly JAVA API" hedges unnecessarily — a `java/` directory exists in the repo.

---

### `docs/Java.md`

**Status:** needs-update

- **Wrong method name — `toBool()`:** Line 36 lists `Bool toBool()` in the condition-to-type function table. The actual method in `java/src/org/rcdb/model.kt:132` is `fun toBoolean(): Boolean`. There is no `toBool()` method anywhere in the Java/Kotlin source.
- **Wrong method name and return type — `toDate()`:** Line 39 lists `Date toDate()`. The actual method in `java/src/org/rcdb/model.kt:180` is `fun toTime(): java.sql.Time`. The method name is `toTime()`, not `toDate()`, and the return type is `java.sql.Time`, not `Date`.

---

### `docs/python.md`

**Status:** needs-update

- **Wrong module namespace:** Line 31 states "CLI application lives in `rcdb.cmd` namespace". The actual module is `rcdb.cli` (directory `python/rcdb/cli/`, entry point `rcdb.cli.app:rcdb_cli` in `pyproject.toml`). There is no `rcdb.cmd` anywhere in the codebase.
- **Misspelled command name:** Line 55 refers to "the notorious `rcdn` command" but the script is `rcnd.py` and the command is `rcnd` (letters transposed).
- **Wrong parameter name:** Line 88 documents `get_run(run_number_or_obj)`. The actual parameter name in `provider.py:211` is `run_number` (no `_or_obj` suffix).
- **Incorrectly documented default:** Line 91 documents `create_condition_type(name, value_type, description="")` with `description` defaulting to an empty string. The actual signature at `provider.py:432` is `def create_condition_type(self, name, value_type, description):` — `description` is a required positional argument.
- **Minor:** Line 305 describes the `cli/` directory as containing commands named `rcdb_cli`. The user-facing installed command is `rcdb` (defined in `pyproject.toml [project.scripts]`).

---

### `docs/rcdb-cli.md`

**Status:** needs-update

- **Missing `rcdb add` command group entirely:** The `rcdb add` group (subcommands: `add type, add condition, add file`) is fully implemented in `python/rcdb/cli/add.py` and registered in `app.py:73`, but is completely absent from the documentation. The doc enumerates 8 subcommands and does not mention `add` at all.
- **Documents unregistered `rcdb run` command:** The doc presents `rcdb run` and `rcdb run ls` as a primary subcommand (#5), but `run_command` is never registered in `app.py`. Lines 67-73 of `app.py` register: `ls, repair, db, rp, web, info, add` — no `run`.
- **Inaccurate `--long` flag description:** Lines 108-110 state `--long, -l` "Prints fuller condition information (includes a longer description)". The actual `ls_command` in `ls.py:9-24` accepts `is_long` but never uses it in the function body — the flag is silently ignored and both short/long output are identical.
- **Minor:** Line 30 claims `rcdb` with no subcommand "will attempt to execute the default command (`info`)". In reality (`app.py:56-63`), the default `info` is only invoked when a connection string is provided; otherwise the help text is shown.
- **Minor:** The `rcdb web` section (lines 323-337) does not mention the `--add-db` option, which allows specifying named databases for the database selector in the web UI.

---

### `docs/Search-queries.md`

**Status:** needs-update

- **Entirely wrong `@is_cosmic` expansion:** The doc claims `@is_cosmic` expands to `run_type == 'hd_all.tsg_cosmic' and 'COSMIC' in daq_run and beam_current < 10`. The actual definition in `python/rcdb/alias.py:63` is `'"cosmic" in run_config and beam_current < 1 and event_count > 5000'`. All three conditions in the doc are wrong: `run_type == 'hd_all.tsg_cosmic'` is absent from the alias; `'COSMIC' in daq_run` is absent; the threshold is `beam_current < 1` not `< 10`; and `event_count > 5000` is in the alias but missing from the doc. The expanded query example is equally wrong for the same reasons.
- **Minor typo and malformed link:** Line 26: "Awailable" should be "Available". The link syntax `[Awailable at GluEx wiki|]` mixes Confluence wiki syntax with Markdown and renders as a broken link.

---

### `docs/Select-runs-and-get-values.md`

**Status:** needs-update

- **Python 2 syntax throughout:** All five code examples use Python 2 bare `print` statements: `print table` (line 64), `print event_count, beam_current` (line 88), `print run.number` (line 140), `print run.get_condition_value('event_count')` (lines 166 and 185). These are `SyntaxError` in Python 3.9+.
- **Minor:** Line 133: broken backtick rendering — triple-backtick opens but a single backtick closes.
- **Minor:** Multiple typos in the DEPRECATED preamble: "syntaxis" (syntax), "contraty" (contrary), "beter" (better), "where" (were).
- **Minor:** Cross-reference links on lines 3 and 22 point to the external GitHub wiki (`github.com/JeffersonLab/rcdb/wiki/Select-values`) where the project now has a local equivalent at `docs/get-started/select-values.md`.

---

### `docs/SQLAlchemy.md`

**Status:** needs-update

This document is a ported MediaWiki page that has not been updated for Python 3, SQLAlchemy 2.x, or the current project structure.

- **Wrong attribute name:** Line 22: `condition.values` does not exist on `Condition`. The correct attribute is `condition.value` (singular). `condition.values` raises `AttributeError`.
- **Python 2 syntax throughout:** All print statements across lines 102-311 use bare `print x` syntax — `SyntaxError` in Python 3.
- **Python syntax error in literal:** Line 182: `.filter(Condition.int_value > 100 000)` — space in integer literal is a `SyntaxError`.
- **Missing required argument:** Lines 283-284: `db.create_condition_type("event_count", ConditionType.INT_FIELD)` omits the required `description` positional argument, raising `TypeError`.
- **Non-existent file path:** Lines 275 and 335-336 reference `$RCDB_HOME/python/example_conditions_query.py`. This file does not exist. The closest equivalent is `python/examples/90_advanced_sqlalchemy_query.py`.
- **Stale SQLAlchemy docs links:** All SQLAlchemy links point to `rel_0_9` (version 0.9). The project uses SQLAlchemy 2.0.50. Correct base URL is `https://docs.sqlalchemy.org/en/20/`.
- **Minor — broken Markdown link:** Line 87: URL parentheses contain extra text — invalid Markdown.
- **Minor — MediaWiki markup throughout:** The document uses `'''bold'''`, `''italic''`, `<syntaxhighlight lang="python">`, `=== heading ===`, and `*list` formatting that renders as literal characters in Markdown renderers (lines 37-336).

---

### `docs/website/index.md`

**Status:** needs-update

- **Hardcoded Python version in WSGI path:** Hardcodes `lib/python3.9/site-packages` in a `sys.path.insert`. Since `pyproject.toml` supports Python 3.9-3.14 and RHEL9 ships Python 3.11 by default, this path silently fails on any non-3.9 installation.
- **Database selector dropdown misdescription:** States each dropdown option shows "the database name and a connection hint (e.g. `Production (rcdb@prodhost)`)". The actual template `python/rcdb/web/templates/layouts/base.html:77` renders only `{{ name }}` — no connection hint.

---

### `docs/website/quick-query.md`

**Status:** needs-update

- **Non-standard image syntax:** Line 1: `[[images/web_quick_query_top.png]]` uses GitHub wiki double-bracket syntax. Standard Markdown image syntax must be used for the image to render in Docsify or GitHub Pages.
- **Severely incomplete — entire interface undocumented:** The doc describes only three basic query modes. The actual web interface includes: separate "Run min" / "Run max" fields with run-period dropdown pickers, a full condition query field supporting the query language, a condition type selection modal, standard aliases dropdown, autoComplete.js autocomplete, and localStorage-based form persistence.
- **Stale placeholder text:** Line 10: "More options is upcoming" — the referenced options are already implemented in `python/rcdb/web/templates/run_search_box.html` and `python/rcdb/web/modules/runs.py:213-259`.
- **Minor typo:** Line 6: "Run nubmer" should be "Run number".
- **Minor grammar:** Line 4: "For query now is possible to use:" is ungrammatical.

---

## Obsolete Files

### `docs/DaqConfigParser.md`

**Status:** obsolete (effectively a placeholder with no usable content)

This is a 17-line stub that only shows a sample config file format and one sentence identifying `TRIGGER` as a section. It contains no API documentation, no import paths, no class names, no usage examples, and no description of the actual parsing modules. The codebase has a substantive config parsing implementation:

- `python/rcdb/config_parser.py` — functions `parse_file`, `parse_content`; classes `ConfigFileParseResult`, `ConfigSection`
- `python/halld_rcdb/run_config_parser.py` — class `HallDMainConfigParseResult`; supports ECAL, DIRC, CCAL beyond the legacy parser
- `python/rcdb/halld_daq_config_parser.py` — legacy module `CodaRunLogParseResult`, `CodaRunLogSection`

None of these modules are mentioned. The supported section names (TRIGGER, GLOBAL, FCAL, BCAL, TOF, ST, TAGH, TAGM, PS, PSC, TPOL, CDC, FDC, ECAL, DIRC, CCAL) are never listed. The doc example uses `# (Re)Created::` but real config files use `#! (Re)Created::`. The file should be completely rewritten or replaced with a substantive reference page.

---

## Files Needing Minor Fixes

| File | What to fix |
|---|---|
| `docs/concepts/db-and-api-structure.md` | (1) `File` should be `ConfigurationFile` (actual class name in `model.py:134`); (2) `time` attribute on `Condition` does not exist — actual field is `time_value`; (3) SQL examples link pins stale branch `dev0.9` — should link to `main`. |
| `docs/Creating-condition-types.md` | (1) Code example mixes keyword and positional arg syntax invalidly: `db.create_condition_type(name="my_val", value_type, description)` is a `SyntaxError`; (2) `description` is documented as optional but is a required positional argument in `provider.py:432`. |
| `docs/daq/daq.md` | (1) `coda_parser.py` listed as a DAQ module alongside `update_coda.py` — it is actually part of the `rcdb` library package; (2) `update_run_config.py` section omits that `update.py` imports from the separate `halld_rcdb` package. |
| `docs/Database-Installation.md` | Typo on line 2: "Evironment" should be "Environment". |
| `docs/get-started/installation.md` | (1) PyPI link points to `https://pypi.org/project/rcdb-web/` — the actual package is `rcdb` (correct URL: `https://pypi.org/project/rcdb/`); (2) Typo line 24: "lbrary" should be "library". |
| `docs/Logging.md` | The doc says logs are stored in the `log_records` table. The actual SQLAlchemy model (`model.py:416`) defines `__tablename__ = 'logs'`. |
| `docs/_sidebar.md` | Typo on line 29: `[Muli-Database]` should be `[Multi-Database]`. |
| `docs/website/database-selector.md` | The doc claims the database selector dropdown shows "the database name and a connection hint". The actual template (`base.html:77`) renders only `{{ name }}` — no connection hint. |
| `docs/website/install.md` | (1) Hardcoded `lib/python3.9/site-packages` path in WSGI example (line 131) — fails on Python 3.10+; (2) `python3-pygments` listed as RPM dependency but absent from `pyproject.toml`; (3) Connection string examples use `mysql://` while codebase default is `mysql+pymysql://`; (4) Inline comment says "now is 2025" — stale. |

---

## Up-to-Date Files

No files are fully up-to-date. All 29 audited files contain at least one confirmed issue.

---

## Action Plan

### High Priority (obsolete / functionally misleading)

These issues will cause immediate failures or confusion for users following the documentation.

1. **`docs/DaqConfigParser.md` — rewrite entirely.**
   The file is a placeholder. Write a real reference page documenting `rcdb.config_parser` (parse_file, parse_content, ConfigFileParseResult, ConfigSection) and `halld_rcdb.run_config_parser` (HallDMainConfigParseResult), including import paths, usage examples, and the full list of supported section names.

2. **`docs/SQLAlchemy.md` — convert MediaWiki markup to Markdown and fix all Python 3 errors.**
   The file is full of `'''bold'''`, `<syntaxhighlight>`, `=== heading ===` MediaWiki syntax that renders as literal text. All `print` statements must become `print(...)`. The `condition.values` attribute must be `condition.value`. The integer literal `100 000` must be `100000`. The `create_condition_type` call must include the `description` argument. All SQLAlchemy links must point to the 2.x docs (`https://docs.sqlalchemy.org/en/20/`).

3. **`docs/Search-queries.md` — correct the `@is_cosmic` expansion.**
   The alias expansion shown is completely wrong (all three conditions are incorrect; one actual condition is missing). Replace with the actual definition from `python/rcdb/alias.py:63`: `'"cosmic" in run_config and beam_current < 1 and event_count > 5000'`. Fix the malformed link and "Awailable" typo.

4. **`docs/concepts/connection.md` — fix the `CCDB_CONNECTION` typo.**
   Line 45 says `CCDB_CONNECTION` — this must be `RCDB_CONNECTION`. This is the single most dangerous error in the docs: users setting `CCDB_CONNECTION` will be confused when the connection is silently ignored. Also fix the incomplete `rcdb -c` CLI example, the Python 2 `print` statement, and the wrong `prov` variable name in the C++ snippet.

5. **`docs/Java.md` — correct the two wrong method names.**
   `toBool()` does not exist; the correct method is `toBoolean(): Boolean`. `toDate()` does not exist; the correct method is `toTime(): java.sql.Time`. Any user of the Java API who follows these docs will get a compilation error.

6. **`docs/get-started/python.md` — add `db.create_run(1)` to the code example.**
   The example raises `NoRunFoundError` at runtime without this call. Also remove the unused `datetime` import and correct the file reference to `python/examples/10_create_conditions_basic.py`.

7. **Register `rcdb select` in `python/rcdb/cli/app.py` or remove all documentation of it.**
   At least four doc files (`query-syntax.md`, `select-values.md`, `rcdb-cli.md`, `rcdb2-migration.md`) document `rcdb select` as a usable command, but it is not registered in `app.py`. Either add `rcdb_cli.add_command(select_command)` to `app.py`, or replace all doc references with the correct available commands.

8. **`docs/index.md` — replace non-functional CLI examples.**
   `rcdb 1000 event_count` is not a valid command in the current Click-based CLI. `rcnd --search` does not exist. Replace these with working examples using the actual registered subcommands.

9. **`docs/Adding-condition-values.md` — fix parameter name, add `description` arg, fix code fence, update print syntax, remove Python 2 links.**
   The `name_values` / `key_values` parameter name error affects every example in the file. The missing `description` argument in all `create_condition_type` calls will raise `TypeError`. The broken code fence at line 174 corrupts Markdown rendering.

---

### Medium Priority (needs-update, but not immediately breaking)

10. **`docs/Cpp.md` — fix `prov` → `con`, `WriteConnection` → `WritingConnection`, correct output directory claim, add missing examples.**
    The `prov` variable name error makes the Getting Values snippet non-compilable. The wrong class name will cause confusion. Update the CMake output directory claim to match reality (`cpp/build/`, not `cpp/bin/`). Add the three undocumented examples.

11. **`docs/python.md` — fix `rcdb.cmd` → `rcdb.cli`, `rcdn` → `rcnd`, correct `get_run` signature, correct `create_condition_type` signature.**
    All four are factual errors in the API reference section.

12. **`docs/rcdb-cli.md` — add `rcdb add` documentation, remove or clearly mark `rcdb run` as unregistered, fix `--long` flag description.**
    The `add` command group is the primary way to write conditions via the CLI and is entirely absent from the doc.

13. **`docs/get-started/add-value-python.md` — replace `ConfigurationProvider` with `RCDBProvider` throughout.**
    `ConfigurationProvider` is an empty stub marked obsolete. The doc actively directs users to import and use an obsolete class.

14. **`docs/development/documentation.md` — remove false Doxygen claim, fix broken links, fix stale coverpage reference.**
    The Doxygen claim is the most impactful; a user trying to generate C++ docs from the documented workflow will find no Doxyfile and no CI step.

15. **`docs/development/development.md` — fix broken internal link, remove `CPLUS_INCLUDE_PATH`, add `PYTHONPATH` and `cpp/bin` to PATH docs.**
    The broken link to `development/database-selector.md` (correct path: `website/database-selector.md`) will produce a 404 in Docsify.

16. **`docs/development/rcdb2-migration.md` — fix `rcdb select` claim, `alias` → `aliases` table name, remove Python 3.8 mention.**

17. **`docs/get-started/query-syntax.md` — fix CLI command name, update Python docs link to Python 3, correct `@is_production` alias definition.**

18. **`docs/get-started/select-values.md` — fix example file GitHub paths, fix filename typo, fix Python 2 print, standardize DB name.**

19. **`docs/Select-runs-and-get-values.md` — convert all five `print` statements to Python 3 syntax. Fix broken backtick. Fix typos in preamble.**

20. **`docs/website/quick-query.md` — rewrite to document the actual current web search interface.**
    The doc is a placeholder that does not reflect a single feature of the implemented search UI. Fix image syntax, remove "upcoming" placeholder, document the actual fields and query capabilities.

---

### Low Priority (minor fixes)

21. **`docs/Creating-condition-types.md`** — Fix the syntactically invalid mixed keyword/positional argument example. Correct the documentation of `description` from optional to required.

22. **`docs/Database-Installation.md`** — Fix the single typo "Evironment" → "Environment" (line 2).

23. **`docs/_sidebar.md`** — Fix "Muli-Database" → "Multi-Database" (line 29).

24. **`docs/Logging.md`** — Correct table name: `log_records` → `logs`.

25. **`docs/get-started/installation.md`** — Fix PyPI link to `https://pypi.org/project/rcdb/` and fix "lbrary" typo.

26. **`docs/concepts/db-and-api-structure.md`** — Rename `File` → `ConfigurationFile` in the class list. Replace `time` → `time_value` in the Condition pseudo-code. Update `dev0.9` branch link to `main`.

27. **`docs/daq/daq.md`** — Clarify that `coda_parser.py` is a library module not a DAQ script, and that `halld_rcdb.run_config_parser` is used for HallD config parsing.

28. **`docs/website/database-selector.md` and `docs/website/index.md`** — Remove the false claim about connection hints in the database selector dropdown.

29. **`docs/website/install.md`** — Replace the hardcoded `python3.9` path in the WSGI example with a dynamic version detection pattern. Clarify `python3-pygments` dependency status. Align connection string scheme with codebase default (`mysql+pymysql://`).
