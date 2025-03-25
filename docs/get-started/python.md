# Python Introduction


## Simple Python API Example

Create or connect to an SQLite database, define a condition type, and store some values:

```python
from datetime import datetime
from rcdb.provider import RCDBProvider
from rcdb.model import ConditionType

# 1. Create/connect to an RCDB database (SQLite in this example).
db = RCDBProvider("sqlite:///example.db", check_version=False)

# 2. Create a condition type -- do this only once. If it already exists, you can skip this.
db.create_condition_type("my_val", ConditionType.INT_FIELD, "This is my value")

# 3. Add data to database (run #1, "my_val" = 1000).
db.add_condition(run=1, key="my_val", value=1000)

# ...Replace previous value by passing replace=True
db.add_condition(run=1, key="my_val", value=2000, replace=True)

# 4. Get a condition from database
condition = db.get_condition(run_number=1, key="my_val")

print(condition)
print("value =", condition.value)
print("name  =", condition.name)
```

Running this script produces something like:

```
<Condition id='1', run_number='1', value=2000>
value = 2000
name  = my_val
```

---

## More Actions on Condition Types

List existing condition types in the database:

```python
for ct in db.get_condition_types():
    print(ct.name, ":", ct.description)
```

Example output:

```
my_val : This is my value
```

---

## Getting Run Conditions

A *Run* in RCDB is represented by the `Run` model. You can fetch a run by number and see all its
conditions:

```python
run = db.get_run(1)
print(f"Conditions for run {run.number}:")
for condition in run.conditions:
    print(condition.name, "=", condition.value)
```

Example output:

```
Conditions for run 1:
my_val = 2000
```

---

## Running the Example

1. **Create an empty SQLite** DB:
   ```bash
   rcdb -c sqlite:///example.db db init
   ```

2. **Run** the sample script above (e.g. `example_conditions_basic.py`):
   ```bash
   python example_conditions_basic.py
   ```

3. **Observe** its output in the console.
   > If you run the script multiple times and you use `replace=True`, you can overwrite old
   condition values.  
   > If you prefer a fresh start, remove `example.db` and re-initialize.


## Summary

- Use **`RCDBProvider(connection_string)`** in Python to connect to or create a DB.
- Create condition types **once** (e.g. `db.create_condition_type("my_val", ...)`).
- **Add conditions** to runs via `db.add_condition(run, "my_val", value, replace=True/False)`.
- **Retrieve** conditions with `db.get_condition(run, "my_val")` or via
  `db.get_run(run).conditions`.
- Manage, query, and explore data with the `rcdb` command-line tool.

This updated guide should help you quickly get started with creating, storing, and retrieving run
conditions in Python 3 for RCDB 2.x. If you have a legacy RCDB 1.x database, you should migrate or
initialize a fresh database as described in the earlier documentation.