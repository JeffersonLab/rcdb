

=== Reusing objects ===


Most of the API functions (like <code>add_condition(...)</code> or  <code>get_condition(...)</code>) can accept model objects as
parameters:

<syntaxhighlight lang="python">
# 1. Using run number and condition name
db.add_condition(1, "my_value", 10)

# 2. Using model objects
run = db.get_run(1)
ct = db.get_condition_type("my_value")
db.add_condition(run, ct, 10)
</syntaxhighlight>


When you do <code>db.add_condition(1, "my_value", 10)</code> condition type and run are queried inside a function. If you do several actions with one object, like adding many conditions for one run or adding one condition to many runs, reusing the object could boost performance up to 30% each.





=== Auto commit value addition===
Performance study shows, that approximately 50% of the time spent in <code>add_condition(...)</code> is used to commit changes to DB.

To speed up conditions addition <code>add_condition(...)</code> function has '''auto_commit''' optional argument.
By default it is '''True''', changes are committed to DB, if ''add_condition'' call is successful.
Setting ''auto_commit''='''False''' allows to defer commit, changes are pending in SQLAlchemy cache and can be committed
manually later.


''auto_commit''='''False''' purposes are:

* Make a lot of changes and commit them at one time gaining performance
* Rollback changes


To commit changes, having <code>db = RCDBProvider(...)</code> you should call <code>db.session.commit()</code>


<syntaxhighlight lang="python">
""" Test auto_commit feature that allows to commit changes to DB later"""
ct = self.db.create_condition_type("ac", ConditionType.INT_FIELD)

# Add condition to addition but don't commit changes
self.db.add_condition(1, ct, 10, auto_commit=False)

# But the object is selectable already
val = self.db.get_condition(1, ct)
self.assertEqual(val.value, 10)

# Commit session. Now "ac"=10 is stored in the DB
self.db.session.commit()

# Now we deffer committing changes to DB. Object is in SQLAlchemy cache
self.db.add_condition(1, ct, 20, None, True, False)
self.db.add_condition(1, ct, 30, None, True, False)

# If we select this object, SQLAlchemy gives us changed version
val = self.db.get_condition(1, ct)
self.assertEqual(val.value, 30)

# Roll back changes
self.db.session.rollback()
val = self.db.get_condition(1, ct)
self.assertEqual(val.value, 10)
</syntaxhighlight>


The example is available in tests:

<pre>
$RCDB_HOME/python/tests/test_conditions.py
</pre>


(!) note at the same time, that more complex scenarios with not committed objects haven't been tested.

