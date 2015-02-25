================================
 RCDB conditions python tutorial
================================

:Author: Dmitry Romanov <romanov@jlab.org>
:Date: $Date: 2013-02-20 01:10:53 +0000 (Wed, 20 Feb 2013) $
:Description: Description of how to manage RCDB run conditions using python API

.. NOTE:: If you are reading this as HTML, please read
   `<cheatsheet.txt>`_ instead to see the input syntax examples!


Introduction
============
Run conditions is the way to store information related to a run (run number is used to identify the run).
From a simplistic point of view, run conditions are presented in RCDB as **name**-**value** pairs attached to a
run number. For example, **event_count** = **1663** for run **100**.


More versatile options of conditions include:

* A condition can also hold a time information of occurrence **name - value (time)**
* Several conditions of the same type could be attached to the same run (or strictly one per run). So it looks like **name** - **[(value1, time1), (value2, time2), ...]**
* Different types of values are supported

This tutorial covers RCDB conditions python API, which provides complete tooling for conditions management.
The API is developed using SQLAlchemy ORM, which unifies workflow for MySQL and SQLite databases (and many more,
actually). RCDB API hides many complexities of SQLAlchemy and provides simple and very  straightforward functions
to manage conditions. But users can use all power of SQLAlchemy for querying and filtering results if they wish.


Lets see how python code would look for the example above.

Read event_count for run 100::

    # Open SQLite database connection
    db = rcdb.RCDBProvider("sqlite:///path.to.file.db")

    # Read value for run 100
    event_count = db.get_condition(100, "event_count").value

Write event_count=1663 for run 100::

    # Once in a lifetime, create a condition type, that defines event_count
    ct = db.create_condition_type("event_count", ConditionType.INT_FIELD, False)

    # Write condition value to run 100
    db.add_condition(100, "event_count", 1663)


One important mention is that values are really attached to the run. If data is bulky and changes rarely
(value is the same for many runs), it is better not to save it using conditions. RCDB provides file saving mechanism
for such kind of data. Or maybe CCDB fits better in this case.


Installation
============

1. **Get rcdb**
RCDB svn is:
https://halldsvn.jlab.org/repos/trunk/online/daq/rcdb/rcdb


2. **Environment**
There are *environment.bash* or *environment.csh* scripts, which automatically set environment variables for the of rcdb

::

    source environment.bash


The script sets *$RCDB_HOME*, appends *$PYTHONPATH* and *$PATH*


3. **Database**

The main database is considered to be MySQL in counting house. The connection string is::

  mysql://rcdb:<whell_known_pwd>@gluondb/rcdb


SQLite database snapshot is also available at::

  /u/group/halld/Software/rcdb


To experiment with RCDB and examples below, there is create_empty_sqlite.py script in $RCDB_HOME/python folder.
The script creates empty sqlite database. The usage is::

   python $RCDB_HOME/python/create_empty_sqlite.py path_to_database.db


Getting started
===============

Working example
---------------

Lets start with basic working example.


::


  from datetime import datetime
  from rcdb.provider import RCDBProvider
  from rcdb.model import ConditionType

  # Create RCDBProvider object that connects to DB and provide most of the functions
  db = RCDBProvider("sqlite:///example.db")

  # Create condition type
  db.create_condition_type("my_val", ConditionType.INT_FIELD, is_many_per_run=False)

  # Add data to database
  db.add_condition(1, "my_val", 1000)

  # Replace previous value
  db.add_condition(1, "my_val", 2000, replace=True)

  # Get condition from database
  condition = db.get_condition(1, "my_val")

  print condition
  print "value =", condition.value
  print "name  =", condition.name



The script result::

  <Condition id='1', run_number='1', value=2000>
  value = 2000
  name  = my_val


The example also available as::

 $RCDB_HOME/python/example_conditions_basic.py

It is assumed that 'example.db' is SQLite database, created by *create_empty_sqlite.py* script.
To run it::

  python $RCDB_HOME/python/create_empty_sqlite.py example.db
  python $RCDB_HOME/python/example_conditions_basic.py

The next sections will cover this example and give thorough explanation on what is here.

Connection
----------

::

  db = RCDBProvider("sqlite:///example.db")


RCDBProvider is an object that holds database session and provides connect/disconnect functions. It uses connection
strings to pass database parameters to the class.

*RCDBProvider* also carry a lot of functions to manage run condition and other RCDB data. The functions returns
database model objects (described right in the next section). Additional manipulations over this objects could be done
with SQLAlchemy (described later).

For now we consider to use MySQL and SQLite databases. The connection strings for them are::

  #MySQL
  mysql://user_name:password@host:port/database

  #SQLite
  sqlite:///path_to_file

**(!)** Note that because SQLite doesn't have user_name and password, it starts with three slashes ///.
And thus there are four slashes //// in absolute path to file.

More about connections can be found on SQLAlchemy documentation
<http://docs.sqlalchemy.org/en/rel_0_9/core/engines.html#database-urls>

In the example above class constructor is used to connect to database. But there are more connection functions::

  # Create provider without connecting
  db = RCDBProvider()

  # Connect to database
  db.connect("sqlite:///example.db")

  # check connection and get connection string from provider
  if db.is_connected:
      print "connected to:", db.connection_string

  #disconnect from DB
  db.disconnect()

**(!)** Note that connect function doesn't really connect to database. It creates so called *engine* and *session*
objects using the connection string. Thus, connect function raises exceptions if the connection string has wrong format
or there is no required libraries in a system. But if there is no physical connection to MySQL or there is no such
SQLite file, the function doesn't raise eny errors. The errors are raised on first data retrieval in such case.

Data model
----------

Database structure
~~~~~~~~~~~~~~~~~~

At the database level conditions part presented as 3 tables::


   RUNS              CONDITIONS         CONDITION_TYPES
    number    <--     run_num            name
                      type_id     -->    field_type
                      *_value            is_many_per_run
                      time

So when we talk about name-value pair for the run,  this actually means that:

 * Run number and other run information (like times of start and end) is stored in the runs table.
 * Names and type of value are stored in the condition_types table.
 * And, finally, values are stored in the conditions table, each record of it is referenced to a run and to a condition_type.


Python class structure
~~~~~~~~~~~~~~~~~~~~~~

Python API data model classes resembles this structure. There are 3 python classes that you work with:

* **Run** - represents run
* **Condition** - stores data for the run
* **ConditionType** - stores condition name, field type and other


All classes have properties to reference each other. The main properties for conditions management are::



    class Run(ModelBase):
        number                  # int - The run number
        start_time              # datetime - Run start time
        end_time                # datetime - Run end time
        conditions              # list[Condition] - Conditions associated with the run


    class ConditionType(ModelBase):
        name                    # str(max 255) - A name of condition
        value_type              # str(max 255) - Type name. Might be one of ..._FIELD constants below
        is_many_per_run         # bool- True if the value is allowed many times per run
        values                  # query[Condition] - to look condition values for specific runs

        # Constants, used for declaration of value_type
        STRING_FIELD = "string"
        INT_FIELD = "int"
        BOOL_FIELD = "bool"
        FLOAT_FIELD = "float"
        JSON_FIELD = "json"
        BLOB_FIELD = "blob"
        TIME_FIELD = "time"


    class Condition(ModelBase):

        @property
        value                   # int, float, bool or string - attached value depending on type
        time                    # datetime - time related to condition (when it occurred in example)
        run_number              # int - the run number

        text_value              # holds value if type is STRING_FIELD, JSON_FIELD or BLOB_FIELD
        int_value               # holds value if type is INT_FIELD
        float_value             # holds value if type is  FLOAT_FIELD
        bool_value              # holds value if type is  BOOL_FIELD


        run                     # Run - Run object associated with the run_number
        type                    # ConditionType - link to associated condition type
        name -> type.name       # str - link to name of the condition. See ConditionType.name
        value_type -> type. ... # str - link to value type. See ConditionType.value_type

How things are stored in the DB
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
As you may noticed from comments above, in reality data is stored in one of the fields:

=============  ======================================
Storage field  Type
=============  ======================================
text_value     STRING_FIELD, JSON_FIELD or BLOB_FIELD
int_value      INT_FIELD
float_value    FLOAT_FIELD
bool_value     BOOL_FIELD
=============  ======================================

When you call Condition.**value** property, Condition class check its type and return appropriate value.

**Why is it so?** - because we would like to have queries like: *give me runs where event_count > 100 000*. At the
same time we would like to store strings or anything with blobs. To have it, db uses so called hybrid approach to
object-attribute-value model, where if value is int, float, bool or time we store in appropriate field allowing to
use its type when querying. And we store more complex opjects as JSON or blobs... to figure out them lately in example


Condition types
---------------
To store conditions data,  a condition type should be added before. It is done once in a database lifetime. Lets look
*create_condition_type* from the example above with parameter names::

 db.create_condition_type(name="my_val", value_type=ConditionType.INT_FIELD, is_many_per_run=False)


**name** - The first parameter is condition name. If we say "event_count for run 100", "event_count" is that name.
Names are case sensitive. There is no strict naming convention validation in API. There is no built in checking for
spaces, but spaces would definitely make problems so are not recommended.

It is possible to have names like::

 category/sub/name
 category-sub-name
 category-sub_name

Names are just strings. RCDB doesn't provide special treatment of slashes '/' or directories.


**value_type** - The second parameter defines type of the value. It can be one of:

*  ConditionType.STRING_FIELD
*  ConditionType.INT_FIELD
*  ConditionType.BOOL_FIELD
*  ConditionType.FLOAT_FIELD
*  ConditionType.TIME_FIELD
*  ConditionType.JSON_FIELD
*  ConditionType.BLOB_FIELD

More examples of how to use types are presented in the next section


**is_many_per_run** - There are two different behaviours that are assumed to be for run conditions:

* It is reasonable to have strictly one name-value for a run. *total_events* or *target_material* are examples of such
  reasoning. For this case set *is_many_per_run*=False and the API will track that there can be only one value per
  run.
* But in another cases it is reasonable to have **name** - **[(value1, time1), (value2, time2), ...]** data. Hall
  *temperature* or *event_rate* during the run are having such behaviour.  If *is_many_per_run*=False is set,
  then API allows to have different values for different times for one name and one run.


Adding data to database
-----------------------
But before... It is not covered in other sections of manual, but you should know. If you ever want to get Run
object by run_number here is how::

 run = db.get_run(run_number)
 print run.number
 print run.start_time
 print run.end_time
 print run.conditions... # but it is written further

How to query runs is shown far below

Adding basic types: int, float, bool, string
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To store basic types one of the fields should be used:

*  ConditionType.STRING_FIELD
*  ConditionType.INT_FIELD
*  ConditionType.BOOL_FIELD
*  ConditionType.FLOAT_FIELD

Lets example it:
::

  # Create RCDBProvider provider object and connect it to DB
  db = RCDBProvider("sqlite:///example.db")

  # Crete condition types
  db.create_condition_type("int_val", ConditionType.INT_FIELD, False)
  db.create_condition_type("float_val", ConditionType.FLOAT_FIELD, False)
  db.create_condition_type("bool_val", ConditionType.BOOL_FIELD, False)
  db.create_condition_type("string_val", ConditionType.STRING_FIELD, False)

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

The output ::

 1000
 2.5
 True
 test test

Add time information
~~~~~~~~~~~~~~~~~~~~
A time information can be attached to any condition value. Standard python datetime is used for that:
(Lets see the first example)::

 # Create condition type
 db.create_condition_type("my_val", ConditionType.INT_FIELD, False)

 # Add value and time information
 db.add_condition(1, "my_val", 2000, datetime(2015, 10, 10, 15, 28, 12, 111111))

 # Get condition from database
 condition = db.get_condition(1, "my_val")

 print condition
 print "value =", condition.value
 print "name  =", condition.name
 print "time  =", condition.time

The output is::

 <Condition id='1', run_number='1', value=2000>
 value = 2000
 name  = my_val
 time  = 2015-10-10 15:28:12.111111

If time is the only relevant information for a condition, then ConditionType.TIME_FIELD type can be used to create
the condition type. In this case **Condition.value** field will have time information and time can be passed as
value parameter of add_condition function::

    db.create_condition_type("lunch_bell_rang", ConditionType.TIME_FIELD, False)

    # add value to run 1
    time = datetime(2015, 9, 1, 14, 21, 01)
    db.add_condition(1, "lunch_bell_rang", time)

    # get from DB
    val = self.db.get_condition(1, "lunch_bell_rang")
    print val.value
    print val.time

Output::

 2015-09-01 14:21:01
 2015-09-01 14:21:01

Note that val.value and val.time are the same in this example.

Adding multiple values per run
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To add many values of the same type, *is_many_per_run* parameter of *create_condition_type* function should be set to True.
Then you are able to add many condition values per one run, but specifying time for each of them.

**(!)** if *is_many_per_run=True*, then *get_condition* will return a list of Condition objects

Example ::

        # Many condition values allowed for the run (is_many_per_run=True)
        #    1. If run has this condition, with the same value and actual_time the func. DOES NOTHING
        #    2. If run has this conditions but at different time, it adds this condition to DB

        db.create_condition_type("multi", ConditionType.INT_FIELD, True)

        time1 = datetime(2015,9,1,14,21,01, 222)
        time2 = datetime(2015,9,1,14,21,01, 333)

        # First addition to DB. Time is None
        db.add_condition(1, "multi", 2222)

        # Ok. Value for time1 is added to DB
        db.add_condition(1, "multi", 3333, time1)
        db.add_condition(1, "multi", 4444, time2)

        results = db.get_condition(1, "multi")

        # We should get 3 values as:
        # 0: value=2222; time=None
        # 1: value=3333; time=time1
        # 2: value=4444; time=time2
        # lets check it
        print results
        values = [result.value for result in results]
        times = [result.time for result in results]
        print values
        print times

The output::

 [<Condition id='1', run_number='1', value=2222>, <Condition id='2', run_number='1', value=3333>, <Condition id='3', run_number='1', value=4444>]
 [2222, 3333, 4444]
 [None, datetime(2015, 9, 1, 14, 21, 1, 222), datetime(2015, 9, 1, 14, 21, 1, 333)]


Storing arrays and dictionaries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Multiple values per run are NOT intended to store arrays of data.

Best way to store arrays and dictionaries is serializing them to JSON. Use ConditionType.JSON_FIELD for that.
RCDB conditions API doesn't provide mechanisms of converting objects to JSON and from JSON. For arrays it is done
easily by json module.

The example from python 2.7 documentation <https://docs.python.org/2/library/json.html>::

 >>> import json
 >>> json.dumps(['foo', {'bar': ('baz', None, 1.0, 2)}])
  '["foo", {"bar": ["baz", null, 1.0, 2]}]'

 >>> json.loads('["foo", {"bar":["baz", null, 1.0, 2]}]')
  [u'foo', {u'bar': [u'baz', None, 1.0, 2]}]


So, serialization is on your side. It is done to have a better control over serialization. This means that
if condition type is JSON_FIELD, *add_condition* function still awaits string and after you get condition back,
Condition.value contains string.

Example::

  import json
  from rcdb.provider import RCDBProvider
  from rcdb.model import ConditionType

  # Create RCDBProvider provider object and connect it to DB
  db = RCDBProvider("sqlite:///example.db")

  # Create condition type
  db.create_condition_type("list_data", ConditionType.JSON_FIELD, False)
  db.create_condition_type("dict_data", ConditionType.JSON_FIELD, False)

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


The example is located at ::

 $RCDB_HOME/python/example_conditions_store_array.py

As one can mention unicode string is returned as unicode after json deserialization (look at u'x' instead of just 'x').
It is not a problem if you just work with this array, because python acts seamlessly with unicode strings.
As you can see in example, we use usual string "x" in restored_dict["x"] and it just works.

If it is a problem, there is a stackoverlow question on that
<http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python>
Using pyYAML to deserialize to strings looks easy.

Storing custom python objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To save custom python objects to database, jsonpickle package could be used. It is an open source
project available via pip install. It is not shipped with RCDB at the moment.

::

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
 db.create_condition_type("cat", ConditionType.JSON_FIELD, False)


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

The result::

 How cat is stored in DB:
 {"py/object": "__main__.Cat", "name": "Alice", "mice_eaten": 1230}
 Deserialized cat:
 name: Alice
 mice_eaten: 1230

jsonpickle Documentation:
http://jsonpickle.github.io/

jsonpickle installation:

system level::

  pip install jsonpickle

user level::

  pip install --user jsonpickle


STRING_FIELD vs. JSON_FIELD vs. BLOB_FIELD
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
What if data doesn't fit into the string or JSON? There is ConditionType.BLOB_FIELD type.

Concise instruction is much like JSON:

* Set condition type as BLOB_FIELD
* You serialize object whatever you like
* Save it to DB as string
* Load from DB
* Deserialize whatever you like

But what is the difference between STRING_FIELD, JSON_FIELD and BLOB_FIELD?

There is no difference in terms of storing the data. A Condition class, same as a database table, has text_value field
where text/string data is stored. The ONLY difference is how this fields are treated and presented in GUI.

**STRING_FIELD** - is considered to be a just human readable string.

**JSON_FIELD** - is considered to be JSON which is colored and formatted accordingly

**BLOB_FIELD** - is considered to be neither simple string nor JSON. But it is still should converted to some string.
And I hope it will never be used.


Replacing previous values
-------------------------

What if the condition value for this run with this name already exists in the DB?

In general, to replace value **replace=True** parameter should be set in **add_condition**.

For single value per run:
1. If run has this condition, with the same value and time, exception is not raised and function does nothing.
2. If value OR actual_time is different than in DB, function checks 'replace' flag and behave accordingly to it

Example::

   db.add_condition(1, "event_count", 1000)                  # First addition to DB
   db.add_condition(1, "event_count", 1000)                  # Ok. Do nothing, such value already exists
   db.add_condition(1, "event_count", 2222)                  # Error. OverrideConditionValueError
   db.add_condition(1, "event_count", 2222, replace=True)    # Ok. Replacing existing value
   print(db.get_condition(1, "event_count"))
   #   value: 2222
   #   time:  None

   time1 = datetime(2015,9,1,14,21,01, 222)
   time2 = datetime(2015,9,1,14,21,01, 333)
   db.add_condition(1, "timed", 1, time1)        # First addition to DB
   db.add_condition(1, "timed", 1, time1)        # Ok. Do nothing
   db.add_condition(1, "timed", 1, time2)        # Error. Time is different
   db.add_condition(1, "timed", 5, time1)        # Error. Value is different
   db.add_condition(1, "timed", 5, time2, True)  # Ok. Value replaced

   print(db.get_condition(1, "timed"))
   #   value: 5
   #   time:  time2


If many condition values allowed for the run (is_many_per_run=True)
    1. If run has this condition, with the same value and same time the func. DOES NOTHING
    2. If run has this conditions but at different time, it adds this condition to DB
    3. If run has this condition at this time

Example::

    time1 = datetime(2015,9,1,14,21,01, 222)
    time2 = datetime(2015,9,1,14,21,01, 333)
    db.add_condition(1, "event_count", 1000)                  # First addition to DB. Time is None
    db.add_condition(1, "event_count", 1000)                  # Ok. Do nothing, such value already exists
    db.add_condition(1, "event_count", 2222)                  # Error. Another value for time None
    db.add_condition(1, "event_count", 2222, replace=True)    # Ok. Replacing existing value for time None
    db.add_condition(1, "event_count", 3333, time1)           # Ok. Value for time1 is added to DB
    db.add_condition(1, "event_count", 4444, time1)           # Error. Value differs for time1
    db.add_condition(1, "event_count", 4444, time2)           # Ok. Add 444 for time2 to DB

    print(db.get_condition(1, "event_count"))
     # [0: value=2222; time=None
     #  1: value=3333; time=time1
     #  2: value=4444; time=time2]


SQLAlchemy
----------

SQLAlchemy glues the classes and makes it possible to navigate between objects

Lets see a code example::

    # open database
    db = rcdb.RCDBProvider("sqlite:///example.db")

    # get Run object for the run number 1
    run = db.get_run(1)

    # now we have access to all conditions for that run as
    run.conditions

    # get all condition names or all condition values

    names = [condition.name for condition in run.conditions]
    values = [condition.values for condition in run.conditions]

SQLAlchemy makes queries to database if needed. So when you do run = self.db.get_run(1) conditions collection is
not yet loaded from DB. It actually isn't loaded even when we introduced run.conditions. But first time when a real
value is needed, database is queried for all conditions for that run.


Editing or deleting objects
---------------------------
Even if overriding of existing values are possible for RCDB, deleting data or editing existing condition types
considered to be avoided. But sometimes it is needed. Especially at the development/debugging phase

To edit or delete things SQLAlchemy *session* object can be used.

Edit condition type::

   # get condition type
   condition_type = db.get_condition_type("my_var")

   # Change what you need
   condition_type.value_type = ConditionType.JSON_FIELD

   # Calling session commit will save changes to database
   db.session.commit()

Deleting objects is done with session.delete function::

   # Edit condition type
   condition_type = db.get_condition_type("my_var")

   # mark the object for deletion
   db.session.delete(condition_type)

   # Calling session commit will save changes to database
   db.session.commit()


More about session and SQLAlchemy objects manipulation with it can be found on SQLAlchemy documentation
<http://docs.sqlalchemy.org/en/rel_0_9/orm/session_basics.html#basics-of-using-a-session>




Database querying
=================

Raw SQLAlchemy queries
----------------------

First, lets say, that if RCDBProvider gives access to SQLAlchemy session, then it is possible to make use of full power
of SQLAlchemy queries.

Lets say, we want to get all runs with event_count > 100 000
::


  # open database
  db = rcdb.RCDBProvider("sqlite:///example.db")

  # create query
  query = db.session.query(Run).join(Run.conditions).join(Condition.type)\
          .filter(ConditionType.name == "event_count")\
          .filter(Condition.int_value > 100 000)\
          .order_by(Run.number)


  # get count of selected runs
  print query.count()

  # get first run from selected
  print query.first()

  # get all run that matches the creteria
  print query.all()

What happened here.

By first line::

 query = db.session.query(Run).join(Run.conditions).join(Condition.type)\

we say, that we would like to select Run objects (*.query(Run)*), and also that we will use conditions and condition
types (*.join(Run.conditions).join(Condition.type)*).

Then we filter results by saying that we look for event_count that have integer value > 100 000. Finally we ask
results to by ordered by Run.number (*.order_by(Run.number)*)

All these functions (join, filter, order_by, ...) returns Query object so you can stack them as many as needed.

Finally, to get the results, one of query.count(), query.first(), query.one() or query.all() is called.

But there are drawbacks of using raw SQLAlchemy queries:

* First, you see that you have to use int_value to filter conditions.
  That by many means worse than using Condition.value property, that handles type automatically.
* Another drawback is that when you add a little more logic, the query becomes bulky.

Lets imagine next example. We look for run in range 1000 to 2000 with event_count > 10000, some data_value in range 1.2
and 2.4

::

    query = db.session.query(Run).join(Run.conditions).join(Condition.type)\
        .filter(Run.number.between(1000, 2000)\
        .filter(((ConditionType.name == "event_count") & (Condition.int_value > 10000)) |
                ((ConditionType.name == "data_value") & (Condition.float_value.between(1.2, 2.4))))\
        .order_by(Run.number)

    print query.all()

Note that instead of common && and ||, & and | is used. SQLAlchemy overloads this operators to use for comparison.
Note also, that such expressions should be in parentheses. It is possible to use or_ and and_ functions instead, but
it doesn't improve readability.

Querying using RCDB helpers
---------------------------

RCDB ConditionType provide helpful properties to make querying easier.

::

    # get condition type
    t = db.get_condition_type("event_count")

    # select runs where event_count > 1000
    query = t.run_query.filter(t.value_field > 1000)

    print query.all()

What happened?

**run_query** - returns query bootstrap that selects Run objects for given type. So it hides this thing from the raw
query above::

 db.session.query(Run).join(Run.conditions).join(Condition.type) ... .filter(((ConditionType.name == "event_count")


**value_field** - returns right Condition.xxx_value for given type. When you put **t.value_field > 1000** here
ConditionType t looked at his value_type and selected right Condition.int_value to compare

(!) Note that if you use condition_type.run_query, each condition type should has its own query.
Queries can be combined by *union* or *intersect* methods later.

Lets look at the example, where we fill DB with dummy data and then query for runs using the helper properties.
The same example can be found in $RCDB_HOME/python/example_conditions_query.py

::

    # create in memory SQLite database
    db = rcdb.RCDBProvider("sqlite://")
    rcdb.model.Base.metadata.create_all(db.engine)

    # create conditions types
    event_count_type = db.create_condition_type("event_count", ConditionType.INT_FIELD, False)
    data_value_type = db.create_condition_type("data_value", ConditionType.FLOAT_FIELD, False)

    # create runs and fill values
    for i in range(0, 100):
        db.create_run(i)
        db.add_condition(i, event_count_type, i + 950)      #event_count in range 950 - 1049
        db.add_condition(i, data_value_type, (i/100.0) + 1) #data_value in 1 - 2


    """ Demonstrates ConditionType query helpers"""
    event_count_type = db.get_condition_type("event_count")
    data_value_type = db.get_condition_type("data_value")

    # select runs where event_count > 1000
    query = event_count_type.run_query.filter(event_count_type.value_field > 1000).filter(Run.number <=53)
    print query.all()

    # select runs where 1.52 < data_value < 1.7
    query2 = data_value_type.run_query
        .filter(data_value_type.value_field.between(1.52, 1.7))\
        .filter(Run.number < 55)
    print query2.all()

    # combine results of this two queries
    print "Results intersect:"
    print query.intersect(query2).all()
    print "Results union:"
    print query.union(query2).all()

The output is::

 [<Run number='51'>, <Run number='52'>, <Run number='53'>]
 [<Run number='52'>, <Run number='53'>, <Run number='54'>]

 Results intersect:
 [<Run number='52'>, <Run number='53'>]

 Results union:
 [<Run number='51'>, <Run number='52'>, <Run number='53'>, <Run number='54'>]



Here is SQLAlchemy querying tutorial
http://sqlalchemy.readthedocs.org/en/rel_0_9/orm/tutorial.html#querying

And here is SQLAlchemy Query API
http://sqlalchemy.readthedocs.org/en/rel_0_9/orm/query.html


Logging
=======
RCDB have a logging system which stores some information about what is going on in the same database in *'log_records'*
table.

Set **RCDB_USER** environment variable to have your name in logs (or set it manually in API as shown below)

While creating condition types goes to log automatically, all condition values manipulations are not logged.
It is done in assumption, that the dabase will have many runs and each run will have many condition values, so if
each condition value creation will have text log message, the database will be bloated with log records.


From the other point of view, when you do a series of operations with conditions it may be a good idea to left a log
message that could be seen by other users.


Custom data modification by SQLAlchemy, like creating or deleting objects manually with session.commit()
is not logged too, so log notification is left to user here too.

How to left a log record::

  # set RCDB_USER environment variable to give RCDB you user name
  # another option is to give it in constructor
  db = RCDBProvider("sqlite:///example.db", user_name="john")

  # and one more option of setting user name
  db.user_name = "john"

  # simplest log version
  db.add_log_record(None, "Hello everybody! You'll see this message in logs on RCDB site", 0)

First None means there is no specific database object ID for this message.
The last '0' means there is no specific run number for this message




