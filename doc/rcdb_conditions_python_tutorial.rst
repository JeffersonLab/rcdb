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

* A condition can also hold a time information of occurrence
* Several conditions of the same type could be attached to the same run (or strictly one per run)
* Different types of values are supported


Python API provides complete set of tools to manage and work with conditions. It is made using SQLAlchemy ORM,
that simplifies querrying and filtering and unifies workflow for MySQL and SQLite databases (and many more,
actually). Also python API provides functions to make work with conditions very straight forward.


Lets see how python code would look for the example above.

Read event_count for run 100::

    # Open SQLite database connection
    db = rcdb.RCDBProvider("sqlite:///path.to.file.db")

    # Read value for run 100
    event_count = db.get_condition(100, "event_count").value

Write event_count=1663 for run 100::

    # Once a lifetime create a condition type defining event_count options
    ct = db.create_condition_type("event_count", ConditionType.INT_FIELD, False)

    # Write condition to run 100
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
(It is assumed that *create_empty_sqlite* created database is used or one can experiment with other SQLite database)


::


  from datetime import datetime
  from rcdb.provider import RCDBProvider
  from rcdb.model import ConditionType

  # Create RCDBProvider provider object and connect it to DB
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
  time  = 2015-10-10 15:28:12.111111
  Database connection


The example is in file::

  $RCDB_HOME/python/example_basic_conditions.py

To run it::

  python $RCDB_HOME/python/create_empty_sqlite.py example.db
  python $RCDB_HOME/python/example_basic_conditions.py

Connection
----------

::

  db = RCDBProvider("sqlite:///example.db")


RCDBProvider is an object that holds database session and provides connect/disconnect functions. It uses connection
strings to pass database parameters to the class.


For now we consider using MySQL and SQLite databases. The connection strings for them are::

  # mysql
  mysql://user_name:password@host:port/database
  sqlite:///path_to_file

**(!)** note that because SQLite doesn't have user_name and password, it starts with three slashes ///.
And there is four slashes //// if absolute path to file is provided.

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

Note that connect function doesn't really connect to database. It creates so called *engine* and *session*
using the connection string. So connect function raises exceptions that corresponds to a wrong connection string format.
But if, for example, there is no physical connection to MySQL or there is no such SQLite file, the function doesn't
raise eny errors. Errors in such case are raised on first data retrieval from the database.

API functions
-------------
*RCDBProvider* class contains a lot of functions to manage run condition and other RCDB data. The functions returns
database model objects (described right in the next section). Additional manipulations over this objects are done
with SQLAlchemy (described below).


Manage data
===========

Data model
----------

Database structure
~~~~~~~~~~~~~~~~~~

At the database level conditions part presented as 3 tables::


   RUNS              CONDITIONS         CONDITION_TYPES
    number    <--     run_num            name
                      type_id     -->    field_type
                      value              is_many_per_run
                      time

So when we talk about name-value pair for the run,  this actually means that:

 * Run numbers as other run information (like start and end times) is stored in the runs table.
 * Names are stored in the condition_types tables as well as other conditions options.
 * And, finally, values are stored in the conditions table, each record of it is referenced to a run and to some condition_type.


Python class structure
~~~~~~~~~~~~~~~~~~~~~~

Python API classes resembles this structure. There are 3 python classes that you work with:

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
        TIME_FIELD = "time"


    class Condition(ModelBase):
        value                   # int, float, bool or string - attached value
        time                    # datetime - time related to condition (when it occurred in example)
        run_number              # int - the run number

        run                     # Run - Run object associated with the run_number
        type                    # ConditionType - link to associated condition type
        name -> type.name       # str - link to name of the condition. See ConditionType.name
        value_type -> type. ... # str - link to value type. See ConditionType.value_type


Condition types
---------------
Once in a database lifetime condition type should be add to store conditions data in future. Lets look
*create_condition_type* from the example above::

 db.create_condition_type("my_val", ConditionType.INT_FIELD, is_many_per_run=False)


The first parameter is condition name. If we talk about event_count for run 100, "event_count" is that name.

The second parameter defines type of the value. It can be one of:

*  ConditionType.STRING_FIELD
*  ConditionType.INT_FIELD
*  ConditionType.BOOL_FIELD
*  ConditionType.FLOAT_FIELD
*  ConditionType.JSON_FIELD
*  ConditionType.TIME_FIELD

More examples of how to use types are presented in the next section

The third parameter


Adding data to database
-----------------------



Reading data
------------

::

  # Getting type information
  ct = db.get_condition_type("my_val")
  print ct
  print "name =", ct.name
  print "value_type =", ct.value_type

The result is::

  <ConditionType id='1', name='my_val', value_type=int>
  name = my_val
  value_type = int

::

  # Getting Run information
  run = db.get_run(1)

  print run
  print "run_number =", run.number

The result is::

  <Run number='1'>
  run_number = 1

::

  # Get condition from database
  condition = db.get_condition(1, "my_val")

  print condition
  print "value =", condition.value
  print "name  =", condition.name

The result is::

  <Condition id='1', run_number='1', value=2000>
  value = 2000
  name  = my_val

One can use objects as function parameters in most of the cases::

 run = db.get_run(1)
 ct = db.get_condition_type("my_val")
 condition = db.get_condition(1, "my_val")
 condition = db.get_condition(run, "my_val")
 condition = db.get_condition(run, ct)

The examples brings the question, what is the difference between *db.get_condition(1, **"my_val"**)* vs
*db.get_condition(1, **ct**)*. The first version may do (and mayby not) additional query to the database. Which is,
in fact, is not a problem for python scripts.

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

Editing or overriding data
--------------------------
Even if overriding of existing values are possible for RCDB, deleting data or editing existing condition types
considered to be avoided. But sometimes it is needed.

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


Logging
=======
