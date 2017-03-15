from rcdb.provider import RCDBProvider
from rcdb.model import ConditionType


class Cat(object):
    def __init__(self, name):
        self.name = name
        self.mice_eaten = 1230

try:
    import jsonpickle
except ImportError:
    print "no jsonpickle module installed. It is required for this example"
    exit(1)


# Create RCDBProvider provider object and connect it to DB
db = RCDBProvider("sqlite:///example.db")

# Create condition type
db.create_condition_type("cat", ConditionType.JSON_FIELD, "The Cat lives here")


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

