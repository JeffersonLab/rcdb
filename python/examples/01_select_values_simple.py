#   E X A M P L E   1
# 3 Lines to get values!


# import RCDB
from rcdb.provider import RCDBProvider

# connect to DB
db = RCDBProvider("mysql://rcdb@hallddb.jlab.org/rcdb2")

# select values with query
table = db.select_values(['polarization_angle', 'polarization_direction'], run_min=30641, run_max=30653)

#   P R I N T   O U T
print(" run_number, polarization_angle, polarization_direction")
for row in table:
    print(row[0], row[1], row[2])

print("We selected: " + ", ".join(table.selected_conditions))

# table.performance holds info about selection timing
print("It took {:.2f} sec ".format(table.performance['total']))

