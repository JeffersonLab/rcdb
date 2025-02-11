Queries allow to select runs using simple 'python if syntax'. Condition names and aliases are used as variables. Queries are implemented in web GUI, python API and CLI . 

**Example.** Query to get production runs with beam current around 100 uA and 'BCAL' in run_config ( here 'BCAL' is a detector / subsystem in HallD and run_config is a name of a configuration file):

General/web site query:
```
@is_production   and   80 < beam_current < 120   and   'BCAL' in run_config
```

[The result of the query on HallD website](https://halldweb.jlab.org/rcdb/runs/search?runFrom=10000&runTo=20000&q=%40is_production+++and+++80+%3C+beam_current+%3C+120+++and+++%27BCAL%27+in+run_config)

Queries syntax are the same across API-s (which supports queries at all)

python:  
```python
runs = db.select_runs("@is_production and 80 < beam_current < 120 and 'BCAL' in run_config")
```

CLI:  
```bash
>>rcdb sel "@is_production and 80 < beam_current < 120 and 'BCAL' in run_config"
```

## Syntax

Queries use python 'if' syntax. The full python documentation is [here](https://docs.python.org/2/library/stdtypes.html). 

Concise version is: 

* ```<```, ```<=```, ```==```, ```!=```, ```=>```, ```>``` to compare values (same as in C++)

* ```or```, ```and```, ```not``` for logic operators (||, &&, ! in C++)

* ```in``` operator is to check a value or a subarray is present in the array, (arrays or lists in python can be given in square braces ```[]```):
    
    ```python
    5 in radiator_id
    radiator_id in [5, 6, 12]
    ```

* strings must be enclosed in ```'``` - single braces. ```==```, ```!=``` operators can be used to compare two strings, ```in``` operator works for substrings and letters:

    ```python
    run_config == 'FCAL_BCAL_PS_m7.conf'
    'hd_all' in run_type
    ```

## Aliases

One may notice ```@is_production``` in the query example above. ```@``` means 'alias' - predefined set of conditions. For example for HallD ```@is_production``` alias is given as:

```python
run_type in ['hd_all.tsg', 'hd_all.tsg_ps', 'hd_all.bcal_fcal_st.tsg'] and
beam_current > 2 and
event_count > 500000 and
solenoid_current > 100 and
collimator_diameter != 'Blocking'
```
