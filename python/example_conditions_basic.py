import sys

from rcdb.provider import RCDBProvider, destroy_all_create_schema
from rcdb.model import ConditionType

if len(sys.argv) > 1:
    # Open database using connection string from command line argument
    db = RCDBProvider(sys.argv[1])
else:
    # Create in-memory database
    db = RCDBProvider("sqlite://", check_version=False)
    destroy_all_create_schema(db)

# Create condition type
db.create_condition_type("my_val", ConditionType.INT_FIELD, "This is my value")

# create run number 1
db.create_run(1)

# Add data to database
db.add_condition(1, "my_val", 1000)

# Replace previous value
db.add_condition(1, "my_val", 2000, replace=True)

# Get condition from database
condition = db.get_condition(1, "my_val")

print(condition)
print("value =", condition.value)
print("name  =", condition.name)


ct = db.get_condition_type("my_val")
print(ct)
print("name =", ct.name)
print("value_type =", ct.value_type)


# Get all existing conditions names and their descriptions
print("Get all existing conditions names and their descriptions")
for ct in db.get_condition_types():
    print ct.name, ':', ct.description

# Get all existing conditions names and their descriptions
print("Get all existing condition names quicker...")
for ct in db.get_condition_types():
    print ct.name, ':', ct.description


# Getting Run information and conditions
print("Getting Run information and conditions")
run = db.get_run(1)

print(run)
print("run_number =", run.number)

print("Conditions for run {}".format(run.number))
for condition in run.conditions:
    print(condition.name, '=', condition.value)

