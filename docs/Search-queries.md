## Aliases

Aliases - are predefined set of filter expressions. The purpose of aliases is to shorten standard search expressions. Aliases starts with ```@``` sign. 

For example, 
```
@is_cosmic
```
Set to:
```python
run_type == 'hd_all.tsg_cosmic' and 'COSMIC' in daq_run and beam_current < 10
```
One can use it like:
```python
@is_cosmic and magnet_current > 800
```

When the query is executed, this expression will be expanded as:
```python
(run_type == 'hd_all.tsg_cosmic' and 'COSMIC' in daq_run and beam_current < 10) and magnet_current > 800
```



### GlueX standard search aliases
[Awailable at GluEx wiki|]
[Wiki](https://halldweb.jlab.org/wiki/index.php/RCDB_Standard_Searches)