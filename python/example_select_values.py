
#   E X A M P L E   1
# 3 Lines to get values!!!
from rcdb.provider import RCDBProvider

db = RCDBProvider("mysql://rcdb@hallddb.jlab.org/rcdb")

table = db.select_values(['polarization_angle', 'polarization_direction'], runs=[30641, 30653])

#   P R I N T   O U T   1
# Print results
print(" run_number, polarization_angle, polarization_direction")
for row in table:
    print row[0], row[1], row[2]


#   E X A M P L E   2
# select values description

                                                                             # Default value | Descrition
                                                                             #---------------+------------------------------------
table = db. select_values(val_names=['event_count', 'beam_current'],         # []            | List of conditions names to select, empty by default
                          search_str="@is_production and event_count>1000",  # ""            | Search pattern.
                          run_min=30200,                                     # 0             | minimum run to search/select
                          run_max=30301,                                     # sys.maxsize   | maximum run to search/select
                          sort_desc=True,                                    # False         | if True result runs will by sorted descendant by run_number, ascendant if False
                          insert_run_number=True,                            # True          | If True the first column of the result will be a run number
                          runs=None)                                         # None          | a list of runs to search from. In this case run_min and run_max are not used
# Some more remarks
#
# 1. val_names. If val_names is left empty, run numbers will be selected (assuming that insert_run_number=True by default)
#
# 2. search_str. If search_str is left empty, the function doesn't apply filters and just select values \
#                for all runs according to 'run_min', 'run_max' range or 'runs' list
#
# 3. runs. One can insert a list of run_numbers like [30001, 30004, ...] here. Then the search/selection will go through
#          this list instead of  'run_min', 'run_max'
#   P R I N T   O U T   2
# table.selected_conditions === table column titles
print("We selected: " + ", ".join(table.selected_conditions))

for row in table:
    print ("run: {0}   event_count: {1}      {2}".format(row[0], row[1], row[2]))

# table.performance holds info about selection timing
print("It took {:.2f} sec ".format(table.performance['total']))


table = db.select_values(['beam_current'], "@is_production", runs=[30300, 30298, 30286])


#   P R I N T   O U T   2
# table.selected_conditions === table column titles
print("We selected: " + ", ".join(table.selected_conditions))

for row in table:
    print ("run: {0}".format(row[0]))

# table.performance holds info about selection timing
print("It took {:.2f} sec ".format(table.performance['total']))

#   E X A M P L E   2
# Bash one liner
# If one wants to select values from, say, bash script and don't want to create separate python script
# run it witn python -c
# python -c "import rcdb.provider;t=rcdb.provider.RCDBProvider('mysql://rcdb@hallddb.jlab.org/rcdb').select_values(['polarization_angle','polarization_direction'], run_min=30000, run_max=31000);print('\n'.join([' '.join(map(str, r)) for r in t]))"

