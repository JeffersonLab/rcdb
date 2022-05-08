# import RCDB
from rcdb.provider import RCDBProvider

# connect to DB
db = RCDBProvider("mysql://rcdb@hallddb.jlab.org/rcdb")

# select values with query
table = db.select_values(['cdc_gas_pressure'], run_min=41512, run_max=41540)

for row in table:
    (run_number, cdc_gas_pressure) = tuple(row)
    print(f"{run_number}   {cdc_gas_pressure}")
