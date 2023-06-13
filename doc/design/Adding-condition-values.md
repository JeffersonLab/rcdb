## Add values

> A 'condition type' (defining name and type) must be created prior adding values. It is discussed in [previous chapter](Creating condition types) and is included in examples further in this chapters

There are two functions to add condition values to DB. First one is:

```python
def add_condition(run, name, value, replace=False)
```

There is a common situation when one has a collection of values (E.g. after parsing a file), for this case there is a handy function that allows to add many conditions values at one time.

```python
def add_conditions(run, name_values, replace=False)
```

The ```name_values``` could be a dictionary or list of name-value pairs:

```python
# dict
name_values = {"name1":value1, "name2":value2, ...}
# list of tuples
name_values = [("name1",value1), ("name2",value2), ...]
# list of lists
name_values = [["name1",value1], ["name2",value2], ...]
```

**(!) performance:** ```add_conditions``` tries to use as less transactions as possible to check and commit all values. So for it provides a big performance gain vs calling ```add_condition``` for each value separately

### Replace values
What if the condition value for this run with this name already exists in the DB?

In general, to replace value ```replace=True``` parameter should be passed to ```add_condition``` or ```add_conditions```.

If run has this condition, with the same value and time, exception is not raised and function does nothing.

Example:

```python
db.add_condition(1, "event_count", 1000)                  # First addition to DB
db.add_condition(1, "event_count", 1000)                  # Ok. Do nothing, such value already exists
db.add_condition(1, "event_count", 2222)                  # Error. OverrideConditionValueError
db.add_condition(1, "event_count", 2222, replace=True)    # Ok. Replacing existing value
print(db.get_condition(1, "event_count"))
#   value: 2222
#   time:  None
```

## Store different data types

### Basic types: int, float, bool, string

To store basic types one of the fields should be used:

* ```ConditionType.STRING_FIELD```
* ```ConditionType.INT_FIELD```
* ```ConditionType.BOOL_FIELD```
* ```ConditionType.FLOAT_FIELD```


Lets example it:

```python
# Create RCDBProvider provider object and connect it to DB
db = RCDBProvider("sqlite:///example.db")

# Crete condition types
db.create_condition_type("int_val", ConditionType.INT_FIELD)
db.create_condition_type("float_val", ConditionType.FLOAT_FIELD)
db.create_condition_type("bool_val", ConditionType.BOOL_FIELD)
db.create_condition_type("string_val", ConditionType.STRING_FIELD)

# Add values to run 1
db.add_condition(1, "int_val", 1000)
db.add_condition(1, "float_val", 2.5)
db.add_condition(1, "bool_val", True)
db.add_condition(1, "string_val", "test test")

# Read values for run 1 and use them

condition = db.get_condition(1, "int_val")
print condition.value

condition = db.get_condition(1, "float_val")
print condition.value

condition = db.get_condition(1, "bool_val")
print condition.value

condition = db.get_condition(1, "string_val")
print condition.value
```

The output:

```
1000
2.5
True
test test
```

### Time information

ConditionType.TIME_FIELD is used for time fields. Standard python datetime is used for that: (Lets see the first example):

```python
# Create condition type
db.create_condition_type("my_val", ConditionType.TIME_FIELD)

# Add value and time information
db.add_condition(1, "my_val", datetime(2015, 10, 10, 15, 28, 12, 111111))
```



### Arrays and dictionaries

Best way to store arrays and dictionaries is serializing them to JSON. Use ConditionType.JSON_FIELD for that.
RCDB conditions API doesn't provide mechanisms of converting objects to JSON and from JSON at this point.
For arrays it is done easily by json module.


The example from [[https://docs.python.org/2/library/json.html python 2.7 documentation]]:

```
>>> import json
>>> json.dumps(['foo', {'bar': ('baz', None, 1.0, 2)}])
 '["foo", {"bar": ["baz", null, 1.0, 2]}]'

>>> json.loads('["foo", {"bar":["baz", null, 1.0, 2]}]')
 [u'foo', {u'bar': [u'baz', None, 1.0, 2]}]
```

So, serialization is on the users side. It is done to have a better control over serialization.
This means that ***if condition type is JSON_FIELD, ```add_condition``` function awaits string*** and ***after you get condition back, Condition.value contains string***.


Example:

```python
import json
from rcdb.provider import RCDBProvider
from rcdb.model import ConditionType

# Create RCDBProvider provider object and connect it to DB
db = RCDBProvider("sqlite:///example.db")

# Create condition type
db.create_condition_type("list_data", ConditionType.JSON_FIELD)
db.create_condition_type("dict_data", ConditionType.JSON_FIELD)

list_to_store = [1, 2, 3]
dict_to_store = {"x": 1, "y": 2, "z": 3}

# Dump values to JSON and save it to DB to run 1
db.add_condition(1, "list_data", json.dumps(list_to_store))
db.add_condition(1, "dict_data", json.dumps(dict_to_store))

# Get condition from database
restored_list = json.loads(db.get_condition(1, "list_data").value)
restored_dict = json.loads(db.get_condition(1, "dict_data").value)

print restored_list
print restored_dict

print restored_dict["x"]
print restored_dict["y"]
print restored_dict["z"]
python

The output is:

```
[1, 2, 3]
{u'y': 2, u'x': 1, u'z': 3}
1
2
3
```


The example is located at

```
$RCDB_HOME/python/example_conditions_store_array.py
```

and can be run as:
```bash
python $RCDB_HOME/python/create_empty_sqlite.py example.db
python $RCDB_HOME/python/example_conditions_store_array.py
```

As one can mention unicode string is returned as unicode after json deserialization (look at u"x" instead of just "x").
It is not a problem if you just work with this array, because python acts seamlessly with unicode strings.
As you can see in example, we use usual string "x" in restored_dict["x"] and it just works.

If it is a problem, there is a
[[http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python stackoverlow question on that]]

Using pyYAML to deserialize to strings looks easy.



### Custom python objects

To save custom python objects to database, jsonpickle package could be used. It is an open source project available
via pip install. It is not shipped with RCDB at the moment.

```python
from rcdb.provider import RCDBProvider
from rcdb.model import ConditionType
import jsonpickle


class Cat(object):
    def __init__(self, name):
        self.name = name
        self.mice_eaten = 1230


# Create RCDBProvider provider object and connect it to DB
db = RCDBProvider("sqlite:///example.db")

# Create condition type
db.create_condition_type("cat", ConditionType.JSON_FIELD)


# Create a cat and store in in the DB for run 1
cat = Cat('Alice')
db.add_condition(1, "cat", jsonpickle.encode(cat))

# Get condition from database for run 1
condition = db.get_condition(1, "cat")
loaded_cat = jsonpickle.decode(condition.value)

print "How cat is stored in DB:"
print condition.value
print "Deserialized cat:"
print "name:", loaded_cat.name
print "mice_eaten:", loaded_cat.mice_eaten
```

The result:

```
How cat is stored in DB:
{"py/object": "__main__.Cat", "name": "Alice", "mice_eaten": 1230}
Deserialized cat:
name: Alice
mice_eaten: 1230
```


[[http://jsonpickle.github.io jsonpickle Documentation]]

jsonpickle installation:

system level:

```
pip install jsonpickle
```

user level:

```
pip install --user jsonpickle
```



### STRING_FIELD vs. JSON_FIELD vs. BLOB_FIELD

What if data doesn't fit into the string or JSON? There is ConditionType.BLOB_FIELD type.

Concise instruction is much like JSON:

* Set condition type as BLOB_FIELD
* You serialize object whatever you like
* Save it to DB as string
* Load from DB
* Deserialize whatever you like


But what is the difference between STRING_FIELD, JSON_FIELD and BLOB_FIELD?


There is no difference in terms of storing the data. A Condition class, same as a database table, has ''text_value''
field where text/string data is stored. The ONLY difference is how this fields are treated and presented in GUI.

* STRING_FIELD - is considered to be a human readable string.

* '''JSON_FIELD''' - is considered to be JSON, which is colored and formatted accordingly

* '''BLOB_FIELD''' - is considered to be neither very readable string nor JSON. But it is still should converted to some string. And I hope it will never be used.
