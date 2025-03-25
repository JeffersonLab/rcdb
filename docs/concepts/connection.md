## Connection

In order to connect to data source, RCDB uses so called `connection strings`. 
The connection strings have the same form for all API-s and the CLI tools. 
The general form is:

```
dialect://username:password@host:port/database
```

For MySQL and SQLite databases the connection strings are:

```
mysql://user_name:password@host:port/database
sqlite:///path_to_file
```

***(!)*** Note that because SQLite doesn't have user_name and password, it starts with three slashes ///.
And thus there are 4 (four) slashes `////` in an absolute path to file.

```
sqlite:////home/user/example.db
```


**HallD MySQL connection string** (as example)

```
mysql://rcdb@hallddb.jlab.org/rcdb
```

More about connection strings could be found in:

- [rfc1738](https://www.ietf.org/rfc/rfc1738.txt)
- [SQLAlchemy documentation](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls)

<br>

## CLI

For CLI tools the standard is to have ```-c``` or ```--connection``` flag and/or 
```RCDB_CONNECTION``` environment variable

```bash
export CCDB_CONNECTION=mysql://user_name:password@host:port/database
rcdb ls

# is the same as
rcdb -c  
```

## Python

```python
db = RCDBProvider("sqlite:///example.db")
```

RCDBProvider is an object that holds database session and provides connect/disconnect functions. It uses connection strings to pass database parameters to the class. It also also carry functions to manage run condition and other RCDB data.

The functions usually return database model objects (described right in the next section).
Additional manipulations over this objects could be done with SQLAlchemy (described later).

In the example above class constructor is used to connect to database. But there are more connection functions:

```python
# Create provider without connecting
db = RCDBProvider()

# Connect to database
db.connect("sqlite:///example.db")

# check connection and get connection string from provider
if db.is_connected:
    print "connected to:", db.connection_string

#disconnect from DB
db.disconnect()
```

## C++ and Java

C++ and Java have similar class structure. The examples are:

[Java simple example](https://github.com/JeffersonLab/rcdb/blob/main/java/src/javaExamples/SimpleExample.java)

[C++ simple example](https://github.com/JeffersonLab/rcdb/blob/main/cpp/examples/simple.cpp)

```c++
// Connect has RAII approach 
Connection con("mysql://rcdb@hallddb/rcdb");

// Get event_count for run 10173
auto cnd = prov.GetCondition(10173, "event_count");
```

## All API:

**(!)** In some cases the ```connect``` function doesn't really connect to database (for lazy initialization features). Thus, *connect* function raises exceptions if the connection string has wrong format or there is no required libraries in the system. But if there is no physical connection to MySQL or there is no such SQLite file, ***the function doesn't guarantees to raise errors***. The errors are raised on first data retrieval in such case. (The function is more or less the same for all APIs)

