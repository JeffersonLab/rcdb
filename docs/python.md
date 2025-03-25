# Python API

Below is a high-level overview of RCDB’s Python API

## 1. Core Aspects

1. **SQLAlchemy ORM**  
   RCDB uses [SQLAlchemy](https://www.sqlalchemy.org/) under the hood for database interactions.
   The `RCDBProvider` is a central class, that wraps SQLAlchemy’s engine and session management, 
   so you typically  interact with RCDB in a high-level way 
   (CRUD operations on `Run`, `Condition`, `ConditionType`, etc.) rather than dealing with raw SQL.

2. **Schema and Models**  
   Since SQLAlchemy is ORM (Object Relational Mapping) it maps DB data to python objects. 
   So  RCDB’s SQL schema has corresponding python classes:
    - `runs` — Each row is a single run, represented in Python by the `Run` model class.
    - `condition_types` — Defines different named conditions you can attach to runs, such as
      *beam_current* or *solenoid_current*. This is the `ConditionType` model.
    - `conditions` — Stores actual values of those conditions (key/value) for specific runs. This is
      the `Condition` model.
    - Additional tables for files, run periods, logs, and so forth.


3. **Tools** 
   There are additional tools and utilities that comes with RCDB python library. Some of them are 
   the parts of library (like CLI and web), others just come along (scripts, examples, etc.)

   - ***Command line tools*** - `rcdb` command is a part of `rcdb` library. 
     It based on [Click library](https://github.com/pallets/click) 
     with a bit of [Textualize/Rich](https://github.com/Textualize/rich). 
     CLI application lives in `rcdb.cmd` namespace
   
   - ***Flask Web GUI*** - Web browser application that can be run locally as user controlled RCDB GUI, 
     to browse runs, conditions, and run periods in a web interface. 
     Or be installed centrally as RCDB web site (using WSGI and servers like apache or nginx).
     Web GUI comes with main `rcdb` library. It uses [Flask](https://github.com/pallets/flask/) 
     based backend and lives in `rcdb.web` namespace.
   
   - ***DAQ***, The codebase includes scripts to automatically parse CODA logs (`update_coda.py`), parse EPICS
     variables (`update_epics.py`), handle run configuration files (`update_run_config.py`), etc.
     As those scripts are usually experiment dependent they are not part of the core `rcdb` library
     and live in [python/daq](https://github.com/JeffersonLab/rcdb/tree/main/python/daq) folder. 
     One can also use HallD scripts, located at 
     [python/halld_rcdb](https://github.com/JeffersonLab/rcdb/tree/main/python/halld_rcdb) as example. 
    
   - ***Examples***, Could be found at 
     [python/examples](https://github.com/JeffersonLab/rcdb/tree/main/python/examples) folders, and
     unit tests (as sometimes also could be used as a learning tool) could be found at 
     [python/tests](https://github.com/JeffersonLab/rcdb/tree/main/python/tests).
   
   - ***Utilities***, are located in 
     [python/utilities](https://github.com/JeffersonLab/rcdb/tree/main/python/utilities).
     A collection of python scripts that were handful over the years of RCDB use and are there  
     mainly as examples and for backward compatibility. Currently, tools are being ported to  
     `rcdb` command. E.g. look `rcdb repair` group. The notorious `rcdn` command is located at
     [python/utilities/rcnd.py](https://github.com/JeffersonLab/rcdb/tree/main/python/utilities/rcnd.py)

---

## Core Classes and Their Responsibilities

Below are the main classes you will encounter in the `rcdb/` directory.

### `RCDBProvider` (in **rcdb.provider**)

- **Role**: The primary entry point for Python-based interactions. Manages the SQLAlchemy session
  and provides high-level functions to create runs, condition types, add conditions, and perform
  queries.
- **Key Methods**:
    - **`__init__(connection_string, ..., check_version=True)`**  
      Creates an RCDBProvider object. You typically do:
      ```python
      from rcdb import RCDBProvider
  
      mysql_db  = RCDBProvider("mysql://rcdb@localhost/rcdb")   # MySQL
      sqlite_db = RCDBProvider("sqlite:///path/to/db.sqlite")   # or use SQLite:
      ```
      Passing `check_version=False` can skip schema-version checks - 
      it could be useful for testing and some DB operations such as `db update`.    
    - **`connect(connection_string, check_version=True)`**  
      Opens a connection to the underlying DB. You usually do not call this if you used `__init__`
      with a connection string. It exists and is not obsolete for rare obscure scripting cases. 
    - **`disconnect()`**  
      Closes the underlying SQLAlchemy session.
    - **`create_run(run_number)`**  
      Ensures a `Run` with the given number exists, creates it if not present.
    - **`get_run(run_number_or_obj)`**  
      Retrieves a `Run` object by run number or returns it unchanged if you pass in an existing `Run`
      object.
    - **`create_condition_type(name, value_type, description="")`**  
        Registers a new condition type in the DB so you can store that condition for future runs (e.g.
        “target_type”, “beam_energy”). The `value_type` can be:
        - `ConditionType.STRING_FIELD`
        - `ConditionType.INT_FIELD`
        - `ConditionType.FLOAT_FIELD`
        - `ConditionType.BOOL_FIELD`
        - `ConditionType.TIME_FIELD`
        - `ConditionType.JSON_FIELD`
        - `ConditionType.BLOB_FIELD`
    - **`add_condition(run, key, value, replace=False)`**  
      Creates or updates a single condition for a run.
      ```python
      db.add_condition(1001, "beam_current", 120.5)
      ```
    - **`add_conditions(run, key_values, replace=False)`**  
      Bulk version of `add_condition`. Accepts either a list of `(key, value)` pairs or a dict.
    - **`get_condition(run_number, key)`**  
      Gets a single condition (i.e., `Condition` object) for a run and a named condition type.
    - **`select_values(val_names, search_str="", run_min=..., run_max=..., sort_desc=False, runs=None, ...)`**  
      High-level method to query runs and fetch condition values in a single pass. Returns an
      `RcdbSelectionResult` which you can iterate over to get
      `(run_number, cond1_value, cond2_value, ...)`.
    - **`session`**  
      Exposes the underlying SQLAlchemy session if you need to do advanced or custom queries.

### Additional classes

- **`RcdbSelectionResult`** (in **rcdb.provider**)  
  Generally returned by `select_values()`. It is a list-like structure of rows, where each row is
  `[run_number, val1, val2, …]`.
- **`StopWatchTimer`**, `LogRecord`, `Alias`, `RunPeriod`, etc.  
  Supporting or helper classes for timing, logging, or advanced features like run periods.



## Data model

### `Run` (in **rcdb.model**)

- **Role**: Represents a single run (its run number, start time, end time, and any associated
  `Condition`s).
- **Notable Fields**:
    - `Run.number` — The run number (primary key).
    - `Run.start_time` / `Run.end_time` — Timestamps for the run.
    - `Run.conditions` — A list of `Condition` objects attached to that run.
- **Key Utility Methods**:
    - **`get_condition(condition_name)`**  
      Returns the `Condition` object for this run, or `None` if missing.
    - **`get_condition_value(condition_name)`**  
      Returns just the `.value` from `Condition`.
    - **`get_conditions_by_name()`**  
      Builds a dictionary of all conditions for that run by their names.

### `ConditionType` (in **rcdb.model**)

- **Role**: Defines the schema (data type, description, etc.) for a named condition (e.g.,
  “beam_current”).
- **Notable Fields**:
    - `ConditionType.name`
    - `ConditionType.value_type`
    - `ConditionType.description`
- **Key Utility**:
    - **`convert_value(value)`**  
      Internally used to validate or convert a Python object into the correct type (e.g. convert to
      float or parse a time).

### `Condition` (in **rcdb.model**)

- **Role**: Stores an actual condition-value for a specific run.  
  For example, run #12000 has a condition named “beam_current” with float_value=120.5.
- **Key Fields**:
    - `Condition.run_number` → links to the run
    - `Condition.type` → links to a `ConditionType`
    - `Condition.value` → property that checks the `ConditionType` to decide if `text_value`,
      `int_value`, `float_value`, etc. should be used.

### `ConfigurationFile` (in **rcdb.model**)

- **Role**: Some experiments store run configuration or log files in the RCDB for easy reference.
  You can link them to runs via the `files_have_runs` association table.
- **In Practice**: Used by scripts like `update_coda.py` or `update_run_config.py` to store the
  entire config file content in the DB if desired.


---

## Key Workflows: Storing and Reading Data

Below are the typical steps you’ll follow when interacting with RCDB via Python.

### Connecting to the Database

```python
from rcdb import RCDBProvider

# MySQL example:
db = RCDBProvider("mysql://rcdb@your_db_host/rcdb")

# or local SQLite:
db = RCDBProvider("sqlite:///my_local_db.sqlite")
```

### Creating Condition Types

Before adding conditions to runs, you must ensure the condition type is defined:

```python
from rcdb import ConditionType

# Suppose you want to store the beam current as a float
db.create_condition_type(
    "beam_current",
    ConditionType.FLOAT_FIELD,
    "Stores the beam current in nA"
)

# Suppose you want to store whether the run is a production run (true/false)
db.create_condition_type(
    "is_production",
    ConditionType.BOOL_FIELD,
    "True if this run is part of official production"
)
```

If the type already exists but has a different type or description, RCDB may raise an
`OverrideConditionTypeError` to prevent accidental schema mismatches.

### Creating Runs

```python
# Creates a run if it doesn't exist. Otherwise, returns the existing Run object
run_obj = db.create_run(1001)
```

### Adding Conditions to a Run

```python
# Single condition
db.add_condition(1001, "beam_current", 120.5)

# Bulk add: pass a dict or list of (key, value) pairs
db.add_conditions(1001, {
    "beam_current": 120.5,
    "is_production": True,
    "target_type": "LH2"
})
```

When you add a condition, RCDB will:

1. Check that the named condition type (e.g. `"beam_current"`) exists.
2. Convert your given value to the correct type (float, int, bool, etc.).
3. Insert or update the corresponding row in the `conditions` table.

### Querying for Runs

Please see [Select Values](get-started/select-values.md) chapter for more examples. 

Use `db.select_values()` to quickly fetch tabular data of multiple conditions across multiple runs:

```python
table = db.select_values(["beam_current", "target_type"],
                         "@is_production and beam_current>100",
                         run_min=1000, run_max=2000)

print(table.selected_conditions)  # e.g. ['beam_current', 'target_type']

for row in table:
    run_number = row[0]
    beam_current_val = row[1]
    target_type_val = row[2]
    print(run_number, beam_current_val, target_type_val)
```

- The first column is always `run_number` by default.
- The rest are your chosen condition fields in the same order you specified.
- The `@is_production` expression is a simple alias for `is_production` in the expression language
  used by RCDB.

### Using the Underlying SQLAlchemy Session

If you need finer control:

```python
from rcdb.model import Run, Condition, ConditionType
from sqlalchemy import asc

# direct session usage
runs_query = db.session.query(Run).filter(Run.number >= 1000).order_by(asc(Run.number))
for run in runs_query:
    print(run.number)
```

The full schema is declared in `rcdb/model.py`, so you can join tables or do advanced SQLAlchemy
operations. However, the built-in `select_runs()` and `select_values()` typically cover common
tasks.

---

## DAQ Modules

While not strictly needed in everyday usage, the repository includes these modules that showcase how
RCDB is extended:

- **`update_coda.py`**  
  Parses CODA XML logs to extract run-related data (event counts, run types, etc.) and saves them in
  RCDB.
- **`update_epics.py`**  
  Demonstrates pulling EPICS variables for a run (like beam current, solenoid current) and storing
  them in RCDB via `db.add_conditions(...)`.
- **`update_run_config.py` and `update_roc.py`**  
  Show how run configuration files or ROC configuration data can be discovered and attached to runs
  as `ConfigurationFile` records, along with storing specialized conditions.
- **`cli/` directory**  
  Contains Click-based CLI commands (`rcdb_cli`) for listing, repairing, or querying runs from a
  shell. These commands internally use the same `RCDBProvider` and model classes.

---

## Putting It All Together

Here is a short script that connects to an RCDB database, creates some condition types, adds data
for run #1234, and queries it back:

```python
from rcdb import RCDBProvider, ConditionType

# 1) Connect to the DB
db = RCDBProvider("sqlite:///my_rcdb.sqlite", check_version=False)

# 2) Create condition types if needed
db.create_condition_type("beam_current", ConditionType.FLOAT_FIELD, "Beam current (nA)")
db.create_condition_type("solenoid_current", ConditionType.FLOAT_FIELD, "Solenoid current (A)")
db.create_condition_type("is_production", ConditionType.BOOL_FIELD, "Production run?")

# 3) Create a run and add conditions
run_num = 1234
db.create_run(run_num)
db.add_conditions(run_num, {
    "beam_current": 150.0,
    "solenoid_current": 1200.0,
    "is_production": True
})

# 4) Query the run
found_run = db.get_run(run_num)
print("Found run number:", found_run.number)
print("  beam_current =", found_run.get_condition_value("beam_current"))
print("  solenoid_current =", found_run.get_condition_value("solenoid_current"))
print("  is_production =", found_run.get_condition_value("is_production"))

# 5) Searching runs with an expression
results = db.select_runs("beam_current>100 and is_production")
print("Runs with beam_current>100 and is_production:")
for run in results:
    print(" ", run.number)
```

