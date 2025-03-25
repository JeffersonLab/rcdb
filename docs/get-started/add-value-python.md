
## 1. Creating or Connecting to a Database

Use `db init` command to create sqlite DB for experiments

```bash
rcdb -c sqlite:///mydb.sqlite db init
```

---

## 2. Creating Condition Types

**Condition types** define how the condition values are stored and interpreted in the database (int,
float, string, JSON, etc.). Use `db.create_condition_type(...)` to add new ones.

Valid value types are:

- `ConditionType.INT_FIELD`
- `ConditionType.FLOAT_FIELD`
- `ConditionType.STRING_FIELD`
- `ConditionType.BOOL_FIELD`
- `ConditionType.TIME_FIELD`
- `ConditionType.JSON_FIELD`
- `ConditionType.BLOB_FIELD`

```python
from rcdb.model import ConditionType

# Create condition types:
db.create_condition_type("my_int_val", ConditionType.INT_FIELD, "My integer value")
db.create_condition_type("my_str_val", ConditionType.STRING_FIELD, "A descriptive string")
db.create_condition_type("my_bool_val", ConditionType.BOOL_FIELD, "Boolean condition")
db.create_condition_type("my_json_val", ConditionType.JSON_FIELD, "Some JSON-based data")
```

- The third parameter is just a **description** stored in the DB for reference.

**Note**: If you try to recreate an existing condition type with a different definition, you may get
an `OverrideConditionTypeError`.

---

## 3. Creating Runs

RCDB organizes data by **run numbers**. You can create or fetch runs with `db.create_run(...)`.

- If the run number already exists, it returns the existing run.

```python
# Create runs:
db.create_run(1001)
db.create_run(1002)

# Or store a variable:
my_run = db.create_run(2000)
print(f"Created run {my_run.number}")
```

---

## 4. Adding Conditions to Runs

Once you have run entries and condition types, you can **add conditions** (key–value pairs) via:

1. **`db.add_condition(run_number_or_run, condition_name_or_type, value, replace=False)`**
2. **`db.add_conditions(run_number_or_run, [ (name, value), ... ], replace=False)`**
3. **`db.add_conditions(run_number_or_run, { name: value, ... }, replace=False)`**

If `replace=True`, it will overwrite the existing condition for that run if it already exists;
otherwise it will throw an error if trying to override a condition with a different value.

### Example: Single Condition

```python
# Add an integer condition to run 1001
db.add_condition(1001, "my_int_val", 42)

# Add a string condition
db.add_condition(1001, "my_str_val", "Beam on")

# You can also supply the run object directly:
my_run = db.get_run(1002)
db.add_condition(my_run, "my_bool_val", True)
```

### Example: Bulk Conditions

```python
# Using a list of (name, value) pairs:
conditions_list = [
    ("my_bool_val", False),
    ("my_str_val", "Calibration run"),
]
db.add_conditions(1001, conditions_list)

# Or using a dictionary:
conditions_dict = {
    "my_int_val": 202,
    "my_json_val": '{"x":10, "y":20}'  # JSON must be a string
}
db.add_conditions(1002, conditions_dict, replace=True)
```

**Important**:

- If you’re storing JSON data, store it as a *string* that contains valid JSON.
- If you add a condition that already exists on that run, and `replace=False`, an exception (
  `OverrideConditionValueError`) will be raised.

---

## 5. Attaching Files to Runs

To **attach files** (e.g., configuration files, CODA logs) to runs, you can use either:

- **`RCDBProvider`** + manual logic, or
- **`ConfigurationProvider`**, which extends `RCDBProvider` and provides
  `add_configuration_file(...)`.

### 5.1 Using `ConfigurationProvider`

`ConfigurationProvider` is a subclass of `RCDBProvider` that adds handy methods for adding files.
Example:

```python
from rcdb.provider import destroy_all_create_schema, ConfigurationProvider

db = ConfigurationProvider("sqlite://", check_version=False)
destroy_all_create_schema(db)

# Create some runs
db.create_run(1)
db.create_run(2)

# Add a file to run 1:
file_path = "/path/to/my_config.conf"
db.add_configuration_file(run=1, path=file_path)

# Alternatively, inline file content:
conf_content = "some text or XML"
db.add_configuration_file(run=2, path="my_custom_file.conf", content=conf_content)
```

#### Overwriting File Content

- If you re-add a file with the same path, the default `overwrite=False` means it will **not**
  overwrite the existing content.
- Use `overwrite=True` to explicitly replace it.

Example:

```python
db.add_configuration_file(2, "my_custom_file.conf", content="old content", overwrite=True)
db.add_configuration_file(2, "my_custom_file.conf", content="new content", overwrite=True)
```

---

## 6. Reading Data Back

### 6.1 Querying Runs and Conditions

- `db.get_run(1001)` returns a `Run` object for run 1001 (or `None` if not found).
- `run.get_conditions_by_name()` returns a dictionary of condition-name → `Condition` objects.
- `run.get_condition_value("my_int_val")` directly returns the stored value.

**Example**:

```python
my_run = db.get_run(1001)
cond_value = my_run.get_condition_value("my_int_val")
print(cond_value)  # e.g. 42
```

### 6.2 Searching

If you need more advanced searching, see:

- `db.select_runs("some logical expression", run_min, run_max, sort_desc=False)`
- `db.select_values([...condition names...], "logical expression", ...)`

---

## 7. Closing or Reusing the Connection

If you are done with the database session:

```python
db.disconnect()
```

Or simply let the Python script end, and the session will be cleaned up.

---

# Complete Example

Below is a brief end-to-end snippet combining many of these steps:

```python
from rcdb.provider import ConfigurationProvider, destroy_all_create_schema
from rcdb.model import ConditionType

# 1) Connect to or create a new SQLite DB
db = ConfigurationProvider("sqlite://", check_version=False)

# 2) (Optional) Wipe everything and create fresh RCDB schema
destroy_all_create_schema(db)

# 3) Create some condition types
db.create_condition_type("my_int_val", ConditionType.INT_FIELD, "My integer condition")
db.create_condition_type("my_json_val", ConditionType.JSON_FIELD, "Stores JSON data")

# 4) Create runs
db.create_run(1)
db.create_run(2)

# 5) Add conditions
db.add_condition(1, "my_int_val", 100)
db.add_conditions(2, {
    "my_int_val": 999,
    "my_json_val": '{"key": "value"}'
})

# 6) Attach files to runs
db.add_configuration_file(1, "/path/to/file.conf")
db.add_configuration_file(2, "my_other_file.conf", content="inline text", overwrite=True)

# 7) Read back data
run1 = db.get_run(1)
print("Run #1 conditions:")
for cnd in run1.conditions:
    print(f"{cnd.name} = {cnd.value}")

db.disconnect()
```

---

## Additional Tips

- **Error Handling**: Creating an existing condition type or condition with a different definition
  can raise exceptions:
    - `OverrideConditionTypeError`
    - `OverrideConditionValueError`
    - `NoRunFoundError`

- **Performance**: For large inserts, you can:
    - Use `replace=True` to avoid repeated checks.
    - Commit in batches instead of after every condition.
