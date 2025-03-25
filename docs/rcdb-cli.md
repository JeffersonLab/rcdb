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

If run with **no** subcommand, `rcdb` will either:
1. Show the help usage, or
2. Attempt to execute the default command (`info`) if no subcommand is given.

---

## Subcommands

Below are the primary subcommands:

1. **`info`** - Prints summary information about the database
2. **`ls`** - Lists existing **condition types**
3. **`db`** - Database commands (info, init, update)
4. **`rp`** (Run Periods) - view or manage Run periods
5. **`run`** - Show run information
6. **`select`** - Select values
7. **`repair`** - Maintenance commands
8. **`web`** - Run local RCDB web

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

- **`SEARCH`** *(optional)*: Currently not heavily used in the example code.
- **`--long, -l`**: Prints fuller condition information (includes a longer description).

**Example:**

```bash
# Basic usage
rcdb ls

# Long usage
rcdb ls --long
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
    - `--no-defaults` (Don’t create default condition types)
    - `--drop-all`    (Drop all existing RCDB data/tables)
    - `--confirm`     (Skips the interactive prompt for non-production automation)

   **Example:**
   ```bash
   rcdb db init --drop-all --confirm
   ```
   > **Warning**: This will destroy all existing RCDB data in the targeted DB.

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

### 5. `rcdb run`

This command grouping can display details of runs or conditions. In the provided code, the main command seen is `ls`, although it may not be fully wired into `rcdb run` in the final distribution.

**Usage (example)**:
```bash
rcdb run ls [RUN_INDEX] [CONDITION]
```

- **`RUN_INDEX`** *(optional)*: Run number to filter on.
- **`CONDITION`** *(optional)*: Condition name to show.

Internally, it can either:
- Show all conditions for the specified run, or
- Show the value of a specific condition if provided.

*(Note: In some deployments, `rcdb run ls` may not be registered automatically. The code is in `rcdb/cli/run.py`; if you do not see it listed via `rcdb --help`, you may need to add it manually. Check the `rcdb_cli.add_command(...)` lines.)*

---

### 6. `rcdb select`

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
    - **`--dump, -d`**: Dump the table in a simpler textual output rather than a fancy table.
    - **`--desc, -d` / `--asc, -a`**: Sort descending or ascending by run number.  
      *(Note: the code uses `--desc/--asc` toggles but also reuses `-d`, so watch for collisions. Confirm which short option is recognized in your environment.)*

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

---

### 7. `rcdb repair`

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

### 8. `rcdb web`

Starts the **Flask**-based web server to display the RCDB in a browser. Useful for local inspection or a lightweight official deployment.

**Usage:**

```bash
rcdb web
```

**Behavior:**
- Loads the Flask application from `rcdb/web/__init__.py`.
- Reads the connection string from `--connection` or environment variables.
- Runs the web app, typically on `http://127.0.0.1:5000`.

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
- **`run`**: View run info (conditions)
- **`select`**: Filter runs by condition logic
- **`repair`**: Utility fixes (like `evio-files`)
- **`web`**: Launch a Flask UI

Use the `--help` flag on the top-level or any subcommand to get further guidance.