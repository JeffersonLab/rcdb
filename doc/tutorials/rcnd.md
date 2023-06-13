*(!) Important notice:*

Initially it was planned that RCDB should have two commands:  

* ```rcdb``` - to select values and readout the database
* ```arcdb``` - which stands for 'admin rcdb' that allows to add data and manipulate the DB

But because RCDB needed something from the beginning, ```rcnd``` tool was created which has some limited abilities to get data from the database and add new values. ```rcnd``` was planned as a temporary command while a/rcdb commands would be in development. In reality, the development has been slowed down and at this point we have:

* ```rcnd``` - widely used command with pretty limited abilities for getting and adding data to DB
* ```rcdb``` - command that has VERY limited abilities and misleads users becuase of it. 

Solutions? Best would be to participate in RCDB development. 

## RCND


```bash
> export RCDB_CONNECTION=mysql://rcdb@localhost/rcdb
> rcnd --help                            # Gives you self descriptive help
> rcnd -c mysql://rcdb@localhost/rcdb    # -c flag sets connection string from command line
> rcnd                                   # Gives database statistics, number of runs and conditions
```

Output:

```
Runs total: 1387
Last run  : 2472
Condition types total: 9
Conditions:

  components
  component_stats
...
```



### Getting condition names and info

To get all conditions `-l` or `--list` flags are to be used. It shows condition names, types and descriptions (if exists):

```bash
> rcnd -l
components (json)
component_stats (json)
event_count (int) - Run events count
event_rate (float) - Events per sec.
...
```


To get names only use `--list-names`:

```
> rcnd --list-names
components
component_stats
event_count
event_rate
...
```

### Getting value by the run number
To see all conditions and values for a run:

```
> rcnd 1000          # See all recorded values for run 1000
components = (json){"ROCBCAL2": "ROC", "ROCBCAL3": "ROC", "ROCBCAL1":...
component_stats = (json){"ROCBCAL2": {"evt-number": 487, "data-rate": 300....
event_count = 487
rtvs = (json){"%(CODA_ROL1)": "/home/hdops/CDAQ/daq_dev_v0.31/d...
run_config = 'pulser.conf'
run_type = 'hd_bcal_n.ti'
...
```


Add name to get value of the only condition:

```
> rcnd 1000 event_count
487

> rcnd 1000 components
{"ROCBCAL2": "ROC", "ROCBCAL3": "ROC"}
```



### Writing data

Creating condition type (need to be done once):

```
> rcnd --create my_value --type string --description "This is my value"
ConditionType created with name='my_value', type='string', is_many_per_run='False'
```

Where --type is:

* bool, int, float, string - basic types. float is the default
* json - to store arrays or custom objects
* time - to store just time. (You can alwais add time information to any other type)
* blob - binary blob. Don't use it if possible


#### Naming policy (not strict at all):

* Don't use spaces. Use '_' instead
* Full words are better. So 'event_count' is better than evt_cnt
* Max name is 255 character. But please, make them shorter



Write value for run 1000 for condition 'my_value'

```
> rcnd --write "value to write" --replace 1000 my_value
Written 'my_value' to run number 1000
```

Without `--replace` error is raised, if run 1000 already have different value for 'my_value'