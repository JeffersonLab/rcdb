import json
import sys
from rcdb.provider import RCDBProvider, destroy_all_create_schema
from rcdb.model import ConditionType

if len(sys.argv) > 1:
    # Open database from command line argument
    db = RCDBProvider(sys.argv[1])
else:
    # Create in-memory database
    db = RCDBProvider("sqlite://", check_version=False)
    destroy_all_create_schema(db)

# Create run (just in case it is not there)
db.create_run(1)

# Create condition type
db.create_condition_type("list_data", ConditionType.JSON_FIELD, "Data list")
db.create_condition_type("dict_data", ConditionType.JSON_FIELD, "Data dict")

list_to_store = [1, 2, 3]
dict_to_store = {"x": 1, "y": 2, "z": 3}

# Dump values to JSON and save it to DB to run 1
db.add_condition(1, "list_data", json.dumps(list_to_store))
db.add_condition(1, "dict_data", json.dumps(dict_to_store))

# Get condition from database
restored_list = json.loads(db.get_condition(1, "list_data").value)
restored_dict = json.loads(db.get_condition(1, "dict_data").value)

print(restored_list)
print(restored_dict)

print(restored_dict["x"])
print(restored_dict["y"])
print(restored_dict["z"])
