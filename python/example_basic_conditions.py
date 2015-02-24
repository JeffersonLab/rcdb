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

# Add time information to the
db.add_condition(1, "my_val", 2000, datetime(2015, 10, 10, 15, 28, 12, 111111), replace=True)

# Get condition from database
condition = db.get_condition(1, "my_val")

print condition
print "value =", condition.value
print "name  =", condition.name
print "time  =", condition.time


# Getting type information
ct = db.get_condition_type("my_val")
print ct
print "name =", ct.name
print "value_type =", ct.value_type


# Getting Run information
run = db.get_run(1)

print run
print "run_number =", run.number