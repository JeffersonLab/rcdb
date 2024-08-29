
To save data in run conditions, a "condition type" should be created first. It is done once in a database lifetime.
Lets look ''create_condition_type'' from the example above (we add parameter names here):

```python
db.create_condition_type(name="my_val",
                         value_type,
                         description)
```

**name** - The first parameter is condition name. When we say "event_count for run 100", "event_count" is that name.
Names are case sensitive. The API doesn't validate names for any name convension and there is no built in checking for
spaces. But spaces would definitely make problems so are not recommended.

It is possible to have names like:

```python
category/sub/name
category-sub-name
category-sub_name
```

Names are just strings. RCDB doesn't provide special treatment of slashes '/' or directories.


**value_type** - The second parameter defines type of the value. It can be one of:

* ConditionType.STRING_FIELD
* ConditionType.INT_FIELD
* ConditionType.BOOL_FIELD
* ConditionType.FLOAT_FIELD
* ConditionType.TIME_FIELD
* ConditionType.JSON_FIELD
* ConditionType.BLOB_FIELD

More examples of how to use types are presented in the next section


**description** - 255 chars max human readable description, that other users can see. It is optional but it is very good practice to fill it.