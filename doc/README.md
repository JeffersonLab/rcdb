# RCDB

Run Configuration/Conditions Database (RCDB) stores run related information and conditions. It uses MySQL or SQLite databases to store information about runs and provides interfaces to search runs, manage data, automatic CODA integration, etc.

One can consider two main aspects of what conceptually RCDB is designed for: 

1. Add data to database   
2. Provide convenient way to read, introspect and analyze DB stored data providing interfaces:
   - Web site
   - Command line interface (CLI)
   - Python API
   - C++ API
   - Possibly JAVA API

## Concepts 

[daq_concepts](daq/daq_concepts.md ':include')

Software wise:
  
   - Can work with multiple databases (MySQL, SQLite, possibly others)
   - Data queries
   - Administration tools
   - DAQ module tools
   - Introspection tools
   

## Demo:

One can visit HallD RCDB Web site as demo:
https://halldweb.jlab.org/rcdb/

Daily updated SQLite database is available here:
https://halldweb.jlab.org/dist/rcdb.sqlite


## Conditions

Run conditions is the way to store information related to a run (which is identified by run_number everywhere).
From a simplistic point of view, run conditions are presented in RCDB as **name**-**value** pairs attached to a run number. For example, **event_count** = **1663** for run **100**.

One of the major use cases of RCDB is searching for runs matching required conditions. It is done using simple, python-if-like queries. The result of ```event_count > 100000``` is all runs, that, obviously, have **event_count** more than **100000**

Lets see how API-s would look for the examples above.

Python:
```python
import rcdb

# Open SQLite database connection
db = rcdb.RCDBProvider("sqlite:///path.to.file.db")

# Read value for run 100
event_count = db.get_condition(100, "event_count").value

# Select runs 
result = db.select_runs("event_count > 100000")
for run in result:
   print run.number   # Or do whatever you want with runs
```

CLI:

```bash
export RCDB_CONNECTION=mysql://rcdb@localhost/rcdb
rcnd --help                            # Gives you self descriptive help
rcnd 1000 event_count                  # See exact value of 'event_count' for run 1000
rcnd --write 1663 100 event_count      # Write condition value to run 100
rcnd --search "event_count > 500"      # Select runs 

```


What RCDB conditions are not designed for? - They are not designed for large data sets that change rarely (value is the same for many runs).
That is because each condition value is independently saved (and attached) for each run.

In the case of bulk data, it is better to save it using other RCDB options. RCDB provides the files saving mechanism as example.

[//]: # (<img src="demo.png" style="max-height: 300px"/>)
