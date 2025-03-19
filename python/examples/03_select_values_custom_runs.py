# import RCDB
from rcdb.provider import RCDBProvider

# connect to DB
db = RCDBProvider("mysql://rcdb@hallddb.jlab.org/rcdb2")

# Select values using a list of runs instead of range
table = db.select_values(['beam_current'], "@is_production", runs=[30300, 30298, 30286])


#   P R I N T   O U T
print("We selected: " + ", ".join(table.selected_conditions))

for row in table:
    print("run: {0}".format(row[0]))

# table.performance holds info about selection timing
print("It took {:.2f} sec ".format(table.performance['total']))
