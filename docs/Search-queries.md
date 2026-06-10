## Aliases

Aliases - are predefined set of filter expressions. The purpose of aliases is to shorten standard search expressions. Aliases starts with ```@``` sign. 

For example, 
```
@is_cosmic
```
Set to:
```python
"cosmic" in run_config and beam_current < 1 and event_count > 5000
```
One can use it like:
```python
@is_cosmic and magnet_current > 800
```

When the query is executed, this expression will be expanded as:
```python
("cosmic" in run_config and beam_current < 1 and event_count > 5000) and magnet_current > 800
```



### GlueX standard search aliases
[Available at GlueX wiki](https://halldweb.jlab.org/wiki/index.php/RCDB_Standard_Searches)