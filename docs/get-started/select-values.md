- [TL;DR; aka Too long didn't read](#tl-dr)
- [Select and filter](#select-and-filter)
- [All options](#all-options)
- [Result details](#result-details)
- [Performance](#performance)
- [From shell](#from-shell)

## TLDR

Fastest way to select values in 3 lines (using HallD rcdb as example):

```python
# import RCDB
from rcdb.provider import RCDBProvider

# connect to DB
db = RCDBProvider("mysql://rcdb@hallddb.jlab.org/rcdb2")

# select values with query
table = db.select_values(['polarization_angle','beam_current'], "@is_production", run_min=30000, run_max=30050)
```

```table``` will contain 3 columns ```run_number```, ```polarization_angle```, ```beam_current```. Like:

```python
[[30044,  -1.0,  UNKNOWN],
 [30045,  45.0,  PARA   ],
...] 
```

<br>

## Select and filter

The fastest designed way to get values from RCDB is by using ```select_values``` function. 
The full example is here:
[$RCDB_HOME/python/example_select_values.py](https://github.com/JeffersonLab/rcdb/blob/master/python/example_select_values.py)

The simplest usage is to put condition names and a run range:

```python
from rcdb.provider import RCDBProvider

db = RCDBProvider("mysql://rcdb@hallddb.jlab.org/rcdb")

table = db.select_values(['polarization_angle','polarization_direction'], run_min=30000, run_max=30050)

# Print results
print(" run_number, polarization_angle, polarization_direction")
for row in table:
    print row[0], row[1], row[2]
```

output:
```
30044 -1.0 UNKNOWN
30045 45.0 PARA
```
By default, the result is a table with runs numbers in the first column and requested conditions values in other columns. 

<br>

### Filter
It is possible to put [a selection query](Query-syntax) as a second argument [as in the above example](#tl-dr):

```python 
table = db.select_values(['polarization_angle'], "@is_production", run_min=30000, run_max=30050)
```

### Exact run numbers
Instead of using run range one can specify exact run numbers using ```runs``` argument

```python 
table = db.select_values(['event_count'], "@is_production", runs=[30300,30298,30286])
```

<br>

## All options

```python
                                                                             # Default value | Descrition
                                                                             #---------------+------------------------------------
table = db.select_values(val_names=['event_count'],                          # []            | List of conditions names to select, empty by default
                          search_str="@is_production and event_count>1000",  # ""            | Search pattern.
                          run_min=30200,                                     # 0             | minimum run to search/select
                          run_max=30301,                                     # sys.maxsize   | maximum run to search/select
                          sort_desc=True,                                    # False         | if True result runs will by sorted descendant by run_number, ascendant if False
                          insert_run_number=True,                            # True          | If True the first column of the result will be a run number
                          runs=None)                                         # None          | a list of runs to search from. In this case run_min and run_max are not used
```

Remarks:
1. ```val_names```. If ```val_names``` list is empty, run numbers will be selected (assuming that insert_run_number=True by default)

2. ```search_str```. If ```search_str`` is empty, the function doesn't apply filters and just select values for all runs according to ['run_min' - 'run_max'] or 'runs' list


<br>

## Result details

The result of ```select_values``` (called ```table``` in the examples) holds more information than just values. Here some useful fields:

- table.selected_conditions - selected condition names (or call it column titles)
- table.performance['total'] - function execution time

```python
table = db.select_values(['beam_current'], "@is_production", runs=[30300,30298,30286])
print("We selected: " + ", ".join(table.selected_conditions))
print("It took {:.2f} sec ".format(table.performance['total']))
```

result:

```
We selected: run, beam_current
It took 0.14 sec 
```

<br>

## Performance

```select_values``` is the fastest way to search over runs and get tables of values. Before that, RCDB had an API with a chain of functions ```select_runs(...).get_values(...)``` for this, which is still there but is much slower. MUCH SLOWER (~10 times). [More details on select_values vs select_runs comparison](https://github.com/JeffersonLab/rcdb/issues/111)

For the most of the use cases the new [select_values](https://github.com/JeffersonLab/rcdb/wiki/Select-values) function is faster and better than `select_runs`. 

- **faster**, while using python `if` statement syntax for search queries, `select_values` relies on SQL search as much as possible and do only the 
  final selection steps in python. Moreover, it pulls only required values, not the whole run information. 
- **beter output**, `select_values` selects the resulting table of run-numbers and values for specified runs. The table of runs and values is what is needed in 99% of cases.  `select_runs` returns a list of `Run` SQLAlchemy objects. Manipulating over `Run`-s objects usually leads to more queries automatically (implicitly) made to DB. 
- **better introspection**, results of `select_values` also has performance metrics and some other goodies. Not that it is needed for regular users, but
  can help to figure out why something is slow. 

More info about old select runs && get values API: [Select runs & get values DEPRECATED](Select-runs-and-get-values) (python)  

<br>

## From shell  
(Shell one liner)

Suppose one wants to select values in a bash script but doesn't want to create a separate python script.
It is possible to call ```python -c "semicolon;separated;commands"```

Combining everything in such one-liner:

```bash
python -c "import rcdb.provider;t=rcdb.provider.RCDBProvider('mysql://rcdb@hallddb.jlab.org/rcdb').select_values(['polarization_angle','polarization_direction'], run_min=30000, run_max=31000);print('\n'.join([' '.join(map(str, r)) for r in t]))"
```

Shouldn't be there an easier way? It was planned to have ```rcdb sel``` command doing it. But it hasn't been fully implemented yet. If you have a spare time (or student) to contribute, please, contact me (Dmitry)
