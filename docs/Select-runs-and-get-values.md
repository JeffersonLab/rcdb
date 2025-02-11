# [DEPRECATED]

Better use [select_values](https://github.com/JeffersonLab/rcdb/wiki/Select-values). See below why

**Contents:**  
- [Selecting runs and getting values](#selecting-runs-and-getting-values)
   + [Get values](#get-values)
   + [Run range](#run-range)
   + [No filtration](#no-filtration)
   + [Sort order](#sort-order)
- [Iterating over runs and getting conditions](#iterating-over-runs-and-getting-conditions)
   + [Getting runs](#getting-runs)
   + [Get any condition of the run](#get-any-condition-of-the-run)
- [Performance](#performance)

-------

## [DEPRECATED] Kind of... 



For the most of the use cases the new [select_values](https://github.com/JeffersonLab/rcdb/wiki/Select-values) function is faster and better than `select_runs`. 

- **faster**, while using python `if` statement syntaxis for search queries, `select_values` relies on SQL search query as much as possible and do only the  final selection steps in python. Moreover, it selects only required values, increasing the performance. The `select_runs` function contraty to that does a lot of filtering on python side and pulls full runs information. 
- **beter output**, `select_values` selects the resulting table of values for specified runs. The table of runs and values is what is needed in 99% of cases.  `select_runs` returns a list of Run SQLAlchemy objects. Manipulating over Run ORM objects usually leads to more queries. 
- **better introspection**, results of select_values also has performance metrics and some other goodies. Not that it is needed for regular users, but
  can help to figure out why something is slow. 

### Dataset to practice on

To experiment with the examples on this page, one can download daily recreated SQLite database:
https://halldweb.jlab.org/dist/rcdb.sqlite

Using connection string:  
```
sqlite:///<path to file>/rcdb.sqlite
```

Or connect to readonly mysql:  
```
mysql://rcdb@hallddb.jlab.org/rcdb
```

<br>
<br>

### Selecting runs and getting values

<br>

#### Get values

Suppose, one wants to get all event_count-s and beam_current-s for production runs:

```python
import rcdb

# Connect to database
db = rcdb.RCDBProvider("mysql://rcdb@hallddb.jlab.org/rcdb")

# Select runs and get values
table = db.select_runs("@is_production")\
          .get_values(['event_count', 'beam_current'], insert_run_number=True)
print table
```

As the result one gets something like:
```
[
[1023, 3984793, 0.145]
[1024, 4569873, 0.230]
...
]
```
The first column is a run number (we set ```insert_run_number=True``` above). The other two columns are 'event_count' and 'beam_current' as we gave it above. 

If run number is not needed ```insert_run_number``` may be skipped:
```python
table = db.select_runs("@is_production")
          .get_values(['event_count', 'beam_current'])
```

A nice way to iterate the values:

```python
for row in table:
    event_count, beam_current = tuple(row)
    print event_count, beam_current
```

<br>

#### Run range

If one wants to apply a run range, say for a particular run period:
```python
table = db.select_runs("@is_production", 10000, 20000)\
          .get_values(['event_count', 'beam_current'], True)
```

<br>

#### No filtration  
To get values for all runs without filtration a search pattern may be skipped:
```python
table = db.select_runs(run_min=10000, run_max=20000)\
               .get_values(['event_count', 'beam_current'], insert_run_number=True)
```

(note that parameter names are used here, so the python could figure function parameters out)


<br>

#### Sort order  
The table is always sorted by run number. It is just a 'feature' of getting runs DB query (that is under the hood). However, the order in with run numbers are sorted could be changed:
```python
table = db.select_runs(run_min=10000, run_max=20000, sort_desc=True)\
               .get_values(['event_count', 'beam_current'], insert_run_number=True)
```

```sort_desc=True``` - makes rows to be sorted by descending run_number


<br>
<br>

### Iterating over runs and getting conditions

<br>

#### Getting runs  
```select_runs``` function returns ```RunSelectionResult``` object that contains all selected runs and some other information about how the runs where selected. The RunSelectionResult implements ```list``` interface returning ```Run`-s. Thus one can do:

```python
import rcdb
db = rcdb.RCDBProvider("mysql://rcdb@hallddb.jlab.org/rcdb")
result = db.select_runs("@is_production")
for run in result:
    print run.number
```

As one could guess the selected run numbers are printed as the result. 

<br> 

#### Get any condition of the run  
```Run``` has the next useful functions:

```python
def get_conditions_by_name(self):              
    # Get all conditions and returns dictionary of condition.name -> condition
def get_condition(self, condition_name):       
    # Gets Condition object by name if such name condition exist or None
def get_condition_value(self, condition_name): 
    # Gets the condition value if such condition exist or None
```

So one can iterate selected runs and get any desired condition:

```python
import rcdb
db = rcdb.RCDBProvider("mysql://rcdb@hallddb.jlab.org/rcdb")
result = db.select_runs("@is_production")
for run in result:
    print run.get_condition_value('event_count')
```



<br><br>

## Performance  

In the performance point of view, the fastest way to get values by using
```
db.select_runs(...).get_values(...)
```
Because ```get_values``` makes just a single database call to retrieve all values for selected runs.

In case of iterating:
```
result = db.select_runs("@is_production")
for run in result:
    print run.get_condition_value('event_count')
```
Database is queried on each get_condition_value





