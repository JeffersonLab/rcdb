## SQLAlchemy

SQLAlchemy makes link between python classes and related database tables. It loads data from DB to classes and when
objects are changed, can commit changes back to DB. Also SQLAlchemy glues the classes and makes it possible to
navigate between objects.

Lets see a code example:

```python
# open database
db = rcdb.RCDBProvider("sqlite:///example.db")

# get Run object for the run number 1
run = db.get_run(1)

# now we have access to all conditions for that run as
run.conditions

# get all condition names or all condition values

names = [condition.name for condition in run.conditions]
values = [condition.values for condition in run.conditions]
```

SQLAlchemy makes queries to database if needed. So when you do `run = self.db.get_run(1)`, `Run.conditions`
collection is not yet loaded from DB. It actually isn't loaded even when we do like x=run.conditions. But first time
when a real value is needed, database is queried for all conditions for that run.



### Editing or deleting objects

Even if overriding of existing values are possible for RCDB, deleting data or editing existing condition types
considered to be avoided. But sometimes it is needed. Especially at the development/debugging phase.


To edit or delete things SQLAlchemy '''session''' object can be used.


#### Editing

**Edit condition type**

```python
# get condition type
condition_type = db.get_condition_type("my_var")

# Change what you need
condition_type.value_type = ConditionType.JSON_FIELD

# Calling session commit will save changes to database
db.session.commit()
```

**Rename condition**

```python
# get condition type
condition_type = db.get_condition_type("my_var")

# Change what you need
condition_type.name = "new_var"

# Calling session commit will save changes to database
db.session.commit()
```

The magic is that all data for all runs are now accessible by '''new_var'''


### Deleting

Deleting objects is done with session.delete function:

```python
# Edit condition type
condition_type = db.get_condition_type("my_var")

# mark the object for deletion
db.session.delete(condition_type)

# Calling session commit will save changes to database
db.session.commit()
```

More about session and SQLAlchemy objects manipulation with it can be found in
[sql alchemy docs](http://docs.sqlalchemy.org/en/rel_0_9/orm/session_basics.html#basics-of-using-a-session SQLAlchemy documentation)





## Database querying


### Working with runs

If you ever want to get Run object by run_number here is how:

```python
run = db.get_run(run_number)
print run.number
print run.start_time
print run.end_time
print run.conditions... # but it is written further
```

How to query runs is shown far below


### Get runs by number (or intruduction to SQLAlchemy queries)

Lets select all runs with run_number < 100 using SQLAlchemy

```python
# open database
db = rcdb.RCDBProvider("sqlite:///example.db")

# create query
query = db.session.query(Run).filter(Run.number < 100)

# get count of selected runs
print query.count()

# get first run from selected
print query.first()

# get all run that matches the creteria
print query.all()
```

What happened?

'''db.session''' - gets SQLAlchemy ''session'' object

'''.query(Run)''' - here we say, that we want Run objects to be returned. At the same time we say what table we want to query

'''.filter(Run.number < 100)''' - filtering clause

When we've got query ready, we can actually get objects by <code>query.first()</code> or <code>query.all()</code>
(there are actually more) or just count number of runs by <code>query.count()</code>

We can use Run.conditions to get conditions for each run. Lets see more advanced example
<syntaxhighlight lang="python">
# open database
db = rcdb.RCDBProvider("sqlite:///example.db")

# create query
query = db.session.query(Run)
    .filter(Run.number.between(50,55)
    .order_by(desc(Run.number))

# get all such runs
runs = query.all()
for run in runs:
    event_count, = (condition.value for condition in run.conditions if condition.name=='event_count')
</syntaxhighlight>

It works and looks easy. But there is one drawback, each selected run will call one SELECT QUERY to DB to get its
conditions. If might be OK for many cases.



=== Raw SQLAlchemy queries ===

What if we want to select runs by conditions value?


First, lets say, that if RCDBProvider gives access to SQLAlchemy session, then it is possible to make use of full
power of SQLAlchemy queries.


Lets say, we want to get all runs with '''event_count''' > '''100 000'''

<syntaxhighlight lang="python">
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
</syntaxhighlight>


What happened here.

By first line:
<syntaxhighlight lang="python">
query = db.session.query(Run).join(Run.conditions).join(Condition.type)\
</syntaxhighlight>

we say, that we would like to select Run objects ('''.query(Run)'''), and also that we will use conditions
and condition types ('''.join(Run.conditions).join(Condition.type)''').


Then we filter results (.'''filter(...)''') and ask results to by ordered by Run.number ('''.order_by(Run.number)''')


All these functions (join, filter, order_by, ...) returns Query object, that allows to stack them as many as needed.


Finally, to get the results, one of query.count(), query.first(), query.one() or query.all() is called.


But probably you already feel drawbacks of this approach:

* First, you see that you have to use int_value to filter conditions. That by many means worse than using Condition.value property, that handles type automatically.
* Another drawback is that when you add more logic, the query becomes bulky.


Lets imagine next example. We look for run in range 1000 to 2000 with event_count > 10000, some data_value in range 1.2 and 2.4

<syntaxhighlight lang="python">
query = db.session.query(Run).join(Run.conditions).join(Condition.type)\
    .filter(Run.number.between(1000, 2000)\
    .filter(((ConditionType.name == "event_count") & (Condition.int_value > 10000)) |
            ((ConditionType.name == "data_value") & (Condition.float_value.between(1.2, 2.4))))\
    .order_by(Run.number)

print query.all()
</syntaxhighlight>


Note that instead of common '''&&''' and '''||''', '''&''' and '''|''' is used.
SQLAlchemy overloads this operators to use for comparison.

Note also, that such expressions should be in parentheses. It is possible to use '''or_''' and '''and_''' functions
instead, but it doesn't improve the readability.



=== Querying using RCDB helpers ===

RCDB ConditionType provide helpful properties to make querying easier.

<syntaxhighlight lang="python">
# get condition type
t = db.get_condition_type("event_count")

# select runs where event_count > 1000
query = t.run_query.filter(t.value_field > 1000)

print query.all()
</syntaxhighlight>


What happened?

*'''run_query''' - returns query bootstrap that selects Run objects for given type. So it hides this thing from the raw query above:

<syntaxhighlight lang="python">
....query(Run).join(Run.conditions).join(Condition.type) ... .filter(((ConditionType.name == "event_count")
</syntaxhighlight>


*'''value_field''' - returns the right Condition.xxx_value for a given type. When you put '''t.value_field > 1000''' here, ConditionType '''t''' looked at his '''value_type''' and selected the right Condition.int_value to compare


But there is a limitation. Each condition type should has its own query. But queries can be combined by '''union''' or
'''intersect''' methods later.


Lets look at the example, where we fill DB with dummy data and then query for runs using the helper properties. The same example can be found in $RCDB_HOME/python/example_conditions_query.py

<syntaxhighlight lang="python">
# create in memory SQLite database
db = rcdb.RCDBProvider("sqlite://")
rcdb.model.Base.metadata.create_all(db.engine)

# create conditions types
event_count_type = db.create_condition_type("event_count", ConditionType.INT_FIELD)
data_value_type = db.create_condition_type("data_value", ConditionType.FLOAT_FIELD)

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
</syntaxhighlight>

The output is:

<pre>
[<Run number='51'>, <Run number='52'>, <Run number='53'>]
[<Run number='52'>, <Run number='53'>, <Run number='54'>]

Results intersect:
[<Run number='52'>, <Run number='53'>]

Results union:
[<Run number='51'>, <Run number='52'>, <Run number='53'>, <Run number='54'>]
</pre>


More on SQLAlchemy queries in
[http://sqlalchemy.readthedocs.org/en/rel_0_9/orm/tutorial.html#querying SQLAlchemy querying tutorial]
[http://sqlalchemy.readthedocs.org/en/rel_0_9/orm/query.html SQLAlchemy Query API]


The example is available as
<syntaxhighlight lang="bash">
python $RCDB_HOME/python/example_conditions_query.py
</syntaxhighlight>
(It creates inmemory database so there is no need in creaty_empty_sqlite.py)

