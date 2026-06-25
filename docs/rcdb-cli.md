## General Usage

```bash
rcdb [OPTIONS] COMMAND [ARGS]...
```

### Global Options

- **`--user-config PATH`**  
  Overrides the default user config location. Defaults to `~/.rcdb_user`.

- **`-c, --connection CONNECTION_STRING`**  
  Sets the database connection string. E.g. `mysql+pymysql://rcdb@localhost/rcdb`.
    - Can also be provided by the environment variable `RCDB_CONNECTION`.

- **`--config KEY VALUE`**  
  Overrides a config key/value pair from the user config file. Multiple pairs may be provided.

- **`-v, --verbose`**  
  Enables verbose mode.

- **`--version`**  
  Prints version and exits.

- **`--help`**  
  Prints help information (including subcommands).

If run with **no** subcommand, `rcdb` behaves as follows:
1. If a connection string **is** provided (via `-c/--connection` or `RCDB_CONNECTION`), it automatically runs the `info` command.
2. If **no** connection string is provided, it prints the help usage.

---

## Subcommands

Below are the primary subcommands:

1. **`info`** - Prints summary information about the database
2. **`ls`** - Lists existing **condition types**
3. **`db`** - Database commands (info, init, update)
4. **`rp`** (Run Periods) - view or manage Run periods
5. **`select`** - Select/list runs by condition logic
6. **`run`** - Show conditions and files of a single run
7. **`add`** - Add data to the DB (types, conditions, files)
8. **`file`** - Inspect stored configuration/log files and their versions
9. **`repair`** - Maintenance commands
10. **`web`** - Run local RCDB web

Each command may also have its own subcommands and additional options.

---

### 1. `rcdb info`

Prints summary information about the database contents. This includes:

- Number of **condition types**
- Number of **condition values**
- Timestamp of last created/updated condition
- Total **runs** stored
- Total **configuration files**
- The last five runs, if any
- Number of **run periods** and the details of the latest run period

**Usage:**

```bash
rcdb info
```

**Example Output:**
```
Num, condition types: 15
Num. condition values: 34534
Last condition date/time: 2025-03-10 11:36:05
Number of runs: 1200
Number of files: 84
Last 5 runs saved: 3050, 3049, 3048, 3047, 3046
Number of run periods: 8
Last Run Period:
  Name:        RunPeriod-2025-03
  Description: 2025 spring beam
  Run Range:   3000 - 3499
  Start Date:  2025-03-01
  End Date:    2025-04-01

run 'rcdb --help' for the list of available commands
```

---

### 2. `rcdb ls`

Lists existing **condition types** (not runs). It can optionally print more detailed information.

**Usage:**

```bash
rcdb ls [SEARCH] [OPTIONS]
```

- **`SEARCH`** *(optional)*: Substring filter applied to condition type names (only matching names are shown).
- **`--long, -l`**: Accepted for backward compatibility, but **currently has no effect** — the output is identical with or without it.

**Example:**

```bash
# Basic usage
rcdb ls

# Filter by name substring
rcdb ls beam
```

**Typical Output:**
```
one                    Some description for condition 'one'
two                    Condition for ...
three                  ...
```

---

### 3. `rcdb db`

Manages global database schema operations such as **initialization** and **updates**. It also can print table size info for MySQL or SQLite.

**Usage:**

```bash
rcdb db [COMMAND]
```

#### Subcommands

1. **`rcdb db init`**  
   Creates RCDB schema in the database.
    - By default, it also creates “default condition types” unless `--no-defaults` is used.
    - Can optionally **drop existing** RCDB data first if `--drop-all` is provided.

   **Options**:
    - `--no-defaults`   (Don’t create default condition types)
    - `--drop-all`      (Drop all existing RCDB data/tables)
    - `--confirm`       (Skips the interactive prompt for non-production automation)
    - `--add-tests`     (Seed the generic unit-test dataset: condition types `a`-`g`)
    - `--add-cpp-tests` (Seed the C++ test fixture: `int_cnd = 5` for run 1, etc.)

   **Example:**
   ```bash
   rcdb db init --drop-all --confirm
   ```
   > **Warning**: This will destroy all existing RCDB data in the targeted DB.

   The `--add-tests` / `--add-cpp-tests` flags make `rcdb db init` the single,
   canonical way to create *and* populate a SQLite database for testing - for
   example the C++ test suite's fixture:
   ```bash
   rcdb -c sqlite:///cpp_test.sqlite db init --add-cpp-tests --confirm
   ```

2. **`rcdb db update`**  
   Updates the database schema from a previous version to a newer one.
    - Typically used only to go from an older RCDB schema (e.g., v1) to the newer one (v2).

   **Example:**
   ```bash
   rcdb db update
   ```

If run **without** a subcommand, `rcdb db` tries to connect and then prints:
- Current schema version
- (For MySQL/SQLite) approximate table sizes in MB

**Example:**

```bash
rcdb db
```

**Sample Output:**
```
Schema version: 2 - 'RCDB Schema v2'
Table sizes in MB (MySQL):
  runs                          125.00 MB
  conditions                    227.50 MB
  ...
```

---

### 4. `rcdb rp`

Manages **Run Periods** (named ranges of runs, along with optional date ranges).

**Usage:**

```bash
rcdb rp [COMMAND]
```

#### Subcommands

1. **`rcdb rp add`**  
   Adds a new run period.
    - **Required**: `--name`, `--run-min`, `--run-max`
    - **Optional**: `--description`, `--start-date`, `--end-date`

   **Example:**
   ```bash
   rcdb rp add \
       --name "RunPeriod-2025-01" \
       --description "First run period of 2025" \
       --run-min 30000 \
       --run-max 30999 \
       --start-date 2025-01-10 \
       --end-date   2025-02-20
   ```

2. **`rcdb rp rm PERIOD_ID`**  
   Removes an existing run period by integer **ID**.
    - Supports `--yes` to skip the confirmation prompt.

   **Example:**
   ```bash
   rcdb rp rm 15 --yes
   ```

3. **`rcdb rp update PERIOD_ID`**  
   Updates a run period’s fields by ID.
    - **Optional** new fields: `--name`, `--description`, `--run-min`, `--run-max`, `--start-date`, `--end-date`

   **Example:**
   ```bash
   rcdb rp update 15 \
       --name "RunPeriod-2025-02" \
       --start-date 2025-02-15
   ```

If `rcdb rp` is run **without** a subcommand, it lists all existing run periods.

---

### 5. `rcdb select`

Executes more advanced condition-based search queries over runs, optionally returning condition columns.

**Usage:**

```bash
rcdb select [QUERY] [VIEW_OR_RUNS...] [OPTIONS]
```

- **`QUERY`**: A boolean expression referencing condition names.
    - e.g. `"beam_current > 5 and polarization_angle in [45,90]"`
    - You can also use any defined **aliases** (like `@is_production`) if present.

- **`VIEW_OR_RUNS...`**: Additional arguments that can define which conditions to show or which runs to search in. Typically a "view" can be a list of condition names to select.

- **Options**:
    - **`--dump, -d`**: Display results in an export-friendly format (no borders/extra formatting) rather than the default rich table.
    - **`--desc` / `--asc`**: Sort by run number descending or ascending. Default is ascending. These are long-only flags (no short option).

**Examples:**

```bash
# Simple query: get runs from 1000 to 1100 that have "event_count > 1e5"
rcdb select "event_count > 100000" 1000-1100

# Select specific columns from runs that match a query:
rcdb select "@is_production" "event_count beam_current" 2000-3000
```

When you run `rcdb select`, it:
1. Parses the `run_min - run_max` range (if given).
2. Evaluates the `QUERY` expression on the conditions.
3. Returns a table of runs and the requested conditions.

If no view is given, the default columns are `event_count run_config`.

---

### 6. `rcdb run`

Shows information about a **single run**: its time span, its conditions and the
files attached to it.

**Usage:**

```bash
rcdb run RUN_NUMBER [OPTIONS]
```

As a shortcut, `rcdb RUN_NUMBER` (a bare number) is treated as `rcdb run RUN_NUMBER`.

By default the full report is printed:

```
Run 1000: 2025-03-10 11:00:00 - 2025-03-10 12:30:00

CONDITIONS:
   beam_current - 12.5
   comment - line one line two that is really really really lon...
FILES
   important:
        /conf/daq.conf
   other files:
        /conf/notes.log
```

String condition values are flattened (new lines replaced by spaces) and
truncated to the first 50 characters, with `...` appended when truncated.
Files are split into **important** (importance `0`) and **other files**.

**Options** (passing one or more limits the output to just those sections and
drops the section titles):

- **`-i`, `--info`**: Show only the run info line (`start - end`).
- **`-c`, `--conditions`**: Show only conditions (without the `CONDITIONS:` title).
- **`-f`, `--files`**: Show only files (without the `FILES` title).

**Examples:**

```bash
rcdb run 1000          # full report
rcdb 1000              # same thing (shortcut)
rcdb run 1000 -i       # just the time span
rcdb run 1000 -c       # just the conditions
rcdb 1000 -f           # just the files
```

---

### 7. `rcdb add`

Adds data to the RCDB: new condition types, condition values for runs, and configuration files attached to runs.

**Usage:**

```bash
rcdb add [COMMAND]
```

#### Subcommands

1. **`rcdb add type NAME`**  
   Adds a new condition type named `NAME`.
    - **`--type`** *(optional, default `float`)*: The data type of the condition. One of `bool`, `int`, `float`, `string`, `json`, `time`, `blob`.
    - **`--description, -d`** *(optional)*: A description for the condition type.

   **Example:**
   ```bash
   rcdb add type beam_current --type=float --description "Beam current in nA"
   ```

2. **`rcdb add condition RUN_NUMBER CONDITION_NAME VALUE`**  
   Adds (or replaces) a condition value for a given run. If the run does not exist it is created. The condition type must already exist (create it first with `rcdb add type`).
    - **`--replace, -r`** *(flag)*: Replace the existing value if one already exists for that run/condition.

   **Example:**
   ```bash
   rcdb add condition 1000 my_value 123.4
   rcdb add condition 1000 event_count 10000 --replace
   ```

3. **`rcdb add file RUN_NUMBER FILE_PATH`**  
   Attaches a configuration file to a run. If the run does not exist it is created. By default the file contents are read from `FILE_PATH` on disk.
    - **`--importance, -i`** *(default `0`)*: Importance level of the file.
    - **`--overwrite`** *(flag)*: Overwrite existing content for the same path and run.
    - **`--content`** *(optional)*: Provide the raw content directly instead of reading from `FILE_PATH` on disk.

   **Example:**
   ```bash
   rcdb add file 1000 /path/to/coda_run.log
   rcdb add file 1000 /path/to/config.txt --importance=2 --overwrite
   ```

---

### 8. `rcdb file`

Inspects configuration and log files stored in the RCDB. A single logical file
(identified by its **path**) can have several **versions** over time: every time
its content changes, a new version with a new `sha256` content hash is stored and
associated with the runs that used it.

File names are matched by **exact path**. Use `rcdb file search` to discover the
exact path from a substring.

**Usage:**

```bash
rcdb file [COMMAND]
```

#### Subcommands

1. **`rcdb file vers FILE_NAME`**
   Shows all versions stored for a file, one per line, as:

   ```
   <sha256 hash> - <last run number this version is used>
   ```

   Versions are sorted by their last used run number, descending.

   **Example:**
   ```bash
   rcdb file vers /gluex/calib/main.conf
   ```

2. **`rcdb file cat FILE_NAME [RUN]`**
   Dumps the raw content of a single version of a file (suitable for piping to
   e.g. `grep`). Exactly one selector must be given:
    - a run number, positionally or via `--run` - prints the version used in that run,
    - `--hash=<hash>` - prints the version with that content hash (a unique **prefix** is accepted).

   **Examples:**
   ```bash
   rcdb file cat /gluex/calib/main.conf 1000
   rcdb file cat /gluex/calib/main.conf --run=1000
   rcdb file cat /gluex/calib/main.conf --hash=7aQaXd3M
   rcdb file cat /gluex/calib/main.conf 1000 | grep TRIGGER
   ```

3. **`rcdb file runs FILE_NAME [RUN FILTERS]`**
   Lists every run that uses a file and the version (hash) used in each run, as:

   ```
   <run number> - <file hash>
   ```

    - **Run filters** (all optional): `--run-min`, `--run-max` (a range), `--run` (a single run),
      `--run-period` (a run period name). The range (`--run-min`/`--run-max`), `--run`, and
      `--run-period` are mutually exclusive. With no filter, all runs are listed.
    - **`--asc` / `--desc`**: Sort by run number. Default is `--desc`.
    - **`--limit N`**: Limit the number of rows.

   **Example:**
   ```bash
   # The last 10 runs that used this file
   rcdb file runs /gluex/calib/main.conf --desc --limit=10
   ```

4. **`rcdb file ls [RUN_SPEC] [RUN FILTERS]`**
   Lists all files attached to the selected runs, sorted by file name, as:

   ```
   <file hash> - <file name>
   ```

   The runs can be given either as a single positional `RUN_SPEC` or with the
   same run-filter options as `rcdb file runs` (`--run-min`, `--run-max`,
   `--run`, `--run-period`). The positional form and the options cannot be mixed.
   With no filter, all files are listed.

   `RUN_SPEC` is interpreted in this order:
    - a **run number** (e.g. `1000`) - same as `--run=1000`,
    - a **run range** (e.g. `1000-2000`, `1000-`, `-2000`) - same as `--run-min`/`--run-max`,
    - otherwise a **run period name** (which may itself contain `-`, e.g. `RunPeriod-2025-01`).

   **Example:**
   ```bash
   rcdb file ls 1000                 # files for run 1000
   rcdb file ls 1000-2000            # files for runs 1000..2000
   rcdb file ls RunPeriod-2025-01    # files for a run period
   rcdb file ls --run-period=RunPeriod-2025-01
   ```

5. **`rcdb file search PATTERN`**
   Prints all distinct file names whose path contains `PATTERN` as a substring.
   Matching is case-insensitive.

   **Example:**
   ```bash
   rcdb file search main.conf
   rcdb file search MAIN.CONF
   ```

---

### 9. `rcdb repair`

A grouping of commands to fix or backfill data. One subcommand is:

1. **`rcdb repair evio-files`**
    - Scans run directories for `.evio` files, then updates the database with `evio_files_count` and `evio_last_file` conditions.
    - Can take arguments like `--run-range`, `--mask`, `--save-list`, `--load-list`, `--execute`.

**Usage:**

```bash
rcdb repair evio-files [OPTIONS]
```

Common options:
- **`--run-range MIN-MAX`**: Only operate on runs within `[MIN, MAX]`.
- **`--mask "..."`**: A glob pattern to locate run directories, e.g. `/gluex/data/rawdata/all/Run*`.
- **`--save-list <filename>`**: Instead of immediately updating the DB, save discovered file data as JSON for later usage.
- **`--load-list <filename>`**: Skip scanning the file system. Load the previously saved JSON for processing.
- **`--execute`**: Actually apply the found `evio_files_count` updates to the DB.
    - If omitted, it only prints or dry-runs the results.

---

### 10. `rcdb web`

Starts the **Flask**-based web server to display the RCDB in a browser. Useful for local inspection or a lightweight official deployment.

**Usage:**

```bash
rcdb web [OPTIONS]
```

**Options:**
- **`--add-db NAME=CONNECTION_STRING`**: Register an additional named database, enabling a database selector in the web UI. May be specified multiple times. If no `-c/--connection` is given, the first `--add-db` entry is used as the default database.

**Behavior:**
- Loads the Flask application from `rcdb/web/__init__.py`.
- Reads the connection string from `--connection` or the `RCDB_CONNECTION` environment variable.
- Runs the web app, typically on `http://127.0.0.1:5000`.

**Example:**
```bash
rcdb -c mysql://rcdb@host/rcdb web \
    --add-db "Production=mysql://rcdb@prodhost/rcdb" \
    --add-db "Test=mysql://rcdb@testhost/rcdb_test"
```

---

## Environment Variables

- **`RCDB_CONNECTION`**  
  If set, automatically picked up as the default database connection string, saving you from having to pass `-c` each time.

- **`RCDB_USER_CONFIG`**  
  Allows pointing to a different user config file instead of the default `~/.rcdb_user`.

---

## Typical Workflows & Examples

1. **Initialize a fresh SQLite database**:
   ```bash
   # Wipes data if it already exists, creates schema, and loads default condition types
   rcdb -c sqlite:///my_rcdb.sqlite db init --drop-all --confirm
   ```
2. **List available condition types**:
   ```bash
   rcdb ls
   ```
3. **Query runs**:
   ```bash
   # Search runs in the range 2000-2100 where "event_count > 1e5" and show beam_current + event_count
   rcdb select "event_count > 100000" 2000-2100 "beam_current event_count"
   ```
4. **Add or update run periods**:
   ```bash
   # Create a run period from 30000 to 30999
   rcdb rp add --name MyPeriod --run-min 30000 --run-max 30999 \
       --start-date 2025-01-01 --end-date 2025-01-10 \
       --description "A sample run period"

   # View all run periods
   rcdb rp
   ```
5. **Start local Flask web**:
   ```bash
   rcdb -c sqlite:///my_rcdb.sqlite web
   # In a browser, navigate to http://127.0.0.1:5000
   ```

---

## Getting Help

- **`rcdb --help`**  
  Prints the top-level help, listing global options and available subcommands.

- **`rcdb <subcommand> --help`**  
  Prints help specific to that subcommand.

Example:
```bash
rcdb db --help
```

---

## Summary

The RCDB CLI provides a convenient way to manage and query your Run Conditions Database. Each subcommand targets specific administrative or user-focused tasks:

- **`info`**: Summaries & stats
- **`ls`**: Condition types listing
- **`db`**: Schema init/update
- **`rp`**: Manage run periods
- **`select`**: Filter/list runs by condition logic
- **`run`**: Show a single run's conditions and files (`rcdb <number>` shortcut)
- **`add`**: Add condition types, conditions, and files
- **`file`**: Inspect stored files, versions, and content
- **`repair`**: Utility fixes (like `evio-files`)
- **`web`**: Launch a Flask UI

Use the `--help` flag on the top-level or any subcommand to get further guidance.