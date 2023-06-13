## Database structure explained

![RCDB sql schema](images/schema.png)

The essential database schema is pretty simple and could be split in four groups of tables:

1. Runs. That is where a run numbers and run periods are stored.
2. File storage. Each file has many to many relationship with run numbers.
3. Conditions. Name-value pairs are stored there
4. Meta. Logs and SQL DB schema version

While Run and File storage are pretty simple and self descriptive, Conditions storage requires
additional explanation. 

In terms of RCDB, ```Conditions``` are name-value pairs attached to runs. So it is like:

```
RUN -- NAME -- VALUE
```

The essential RCDB feature is that while all runs may have a common set of name-value pairs (e.g. event_count, run_type), some runs may have special name-value pairs, that are not relevant for other runs. For example one may have trigger study with some trigger specific values that doesn't make sense for physics runs. The same could be imagined for for calibration runs. 

With this feature in mind, it is not optimal to create just one table with all possible conditions as columns and all values as rows (huge rows). Instead, RCDB uses so called "hybrid approach to object-attribute-value model". The are two tables: ```conditions``` that stores actual values and ```condition_types``` that holds information of condition names and their real types. ```conditions``` table has several columns to store different types of values.


| Storage column| Data type |
|---------------|------------|
|text_value     |strings, json, blobs, long texts |
|int_value      |integers  |
|float_value    |floats |
|bool_value     |booleans  |
|time_value     |date time values|

***Why is it so?*** - because we would like to have queries like: *"give me runs where event_count > 100 000"*

i.e., if we know that **event_count* is int, we would like database to treat it as int. At the same time we would like to store strings and more general data with blobs. 

If value is int, float, bool or time, it is stored in appropriate field, which allows to use its type when querying and searching over them. At the same time, more complex objects as JSON or blobs can be stored... to figure out them lately

This approach adds some complexity for its flexibility. But those complexities are minimized by APIs, which automate type checks. So finally users work with just run-name-values, leaving the complexities under the hood of APIs. 

Lets look at python API as an example


<br> 

## Python

Python API data model classes resembles this structure. Most common python classes that you work with:

* **Run** - represents run
* **Condition** - stores data for the run
* **ConditionType** - stores condition name, field type and other


All classes have properties to reference each other. The main properties for conditions management are:

```python
class Run(ModelBase):
    number                  # int - The run number
    start_time              # datetime - Run start time
    end_time                # datetime - Run end time
    conditions              # list[Condition] - Conditions associated with the run


class ConditionType(ModelBase):
    name               # str(max 255) - A name of condition
    value_type         # str(max 255) - Type name. One of XXX_FIELD below
    values             # query[Condition] - query to look condition values for runs

    # Constants, used for declaration of value_type
    STRING_FIELD = "string"
    INT_FIELD = "int"
    BOOL_FIELD = "bool"
    FLOAT_FIELD = "float"
    JSON_FIELD = "json"
    BLOB_FIELD = "blob"
    TIME_FIELD = "time"


class Condition(ModelBase):
    time           # datetime - time related to condition (when it occurred in example)
    run_number     # int - the run number

    @property
    value          # int, float, bool or string - depending on type. The condition value

    text_value     # holds data if type STRING_FIELD,JSON_FIELD or BLOB_FIELD
    int_value      # holds data if type INT_FIELD
    float_value    # holds data if type FLOAT_FIELD
    bool_value     # holds data if type BOOL_FIELD

    run            # Run - Run object associated with the run_number
    type           # ConditionType - link to associated condition type
    name           # str - link to type.name. See ConditionType.name
    value_type     # str - link to type.value_type. See ConditionType.value_type
```


#### How data is stored in the DB 

In general, one just uses Condition.value to get the right value for the condition. But what happens under the hood? 

As you may noticed from comments above, in reality data is stored in one of the fields:

| Storage field | Value type |
|---------------|------------|
|text_value     |STRING_FIELD, JSON_FIELD or BLOB_FIELD |
|int_value      |INT_FIELD   |
|float_value    |FLOAT_FIELD |
|bool_value     |BOOL_FIELD  |
|time_value     |TIME_FIELD  |


When you call **Condition.value** property, Condition class checks for **type.value_type** and returns
an appropriate **xxx_value**.