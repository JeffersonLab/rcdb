At least to start with RCDB conditions, to put values and to get them back:


#Python

```python
from datetime import datetime
from rcdb.provider import RCDBProvider
from rcdb.model import ConditionType

# 1. Create RCDBProvider object that connects to DB and provide most of the functions
db = RCDBProvider("sqlite:///example.db")

# 2. Create condition type. It is done only once
db.create_condition_type("my_val", ConditionType.INT_FIELD, "This is my value")

# 3. Add data to database
db.add_condition(1, "my_val", 1000)

# Replace previous value
db.add_condition(1, "my_val", 2000, replace=True)

# 4. Get condition from database
condition = db.get_condition(1, "my_val")

print(condition)
print("value =", condition.value)
print("name  =", condition.name)

```

The script result:
```
<Condition id='1', run_number='1', value=2000>
value = 2000
name  = my_val
```


More actions on objects:

```python
# 5. Get all existing conditions names and their descriptions
for ct in db.get_condition_types():
    print ct.name, ':', ct.description
```


The script result:
```
my_val : This is my value
```


```python
# 6. Get all values for the run 1
run = db.get_run(1)
print "Conditions for run {}".format(run.number)
for condition in run.conditions:
    print condition.name, '=', condition.value
```


The script result:
<pre>
my_val = 2000
</pre>


The example also available as:

```bash
$RCDB_HOME/python/example_conditions_basic.py
```


It is assumed that 'example.db' is SQLite database, created by *create_empty_sqlite.py* script. To run it:

```bash
python $RCDB_HOME/python/create_empty_sqlite.py example.db
python $RCDB_HOME/python/example_conditions_basic.py

# '''(!)''' note that to run the script again you probably have to delete the database 
# rm example.db

```


The next sections will cover this example and give thorough explanation on what is here.



## Command line tools
Command line tools provide less possibilities for data manipulation than python API at the moment.

```bash
export RCDB_CONNECTION=mysql://rcdb@localhost/rcdb
rcnd --help                            # Gives you self descriptive help
rcnd -c mysql://rcdb@localhost/rcdb    # -c flag sets connection string from command line instead of environment
rcnd                                   # Gives database statistics, number of runs and conditions
rcnd 1000                              # See all recorded values for run 1000
rcnd 1000 event_count                  # See exact value of 'event_count' for run 1000

# Creating condition type (need to be done once)
rcnd --create my_value --type string --description "This is my value"

# Write value for run 1000 for condition 'my_value'
rcnd --write "value to write" --replace 1000 my_value

# See all condition names and types in DB
rcnd --list
```

More information and examples are in [[#Command line tools]] section below.
