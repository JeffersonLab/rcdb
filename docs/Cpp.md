- [Installation](Cpp#installation)  
- [Getting values](Cpp#getting-values)  
- [Examples](Cpp#examples)

## RCDB C++ API overview

C++ API is a header only library that allows to read RCDB condition values for the run. The library doesn't provide possibility of run selection queries at this point. Also it requires C++11 to compile. 

C++ API code is located in [$RCDB_HOME/cpp](https://github.com/JeffersonLab/rcdb/tree/master/cpp) directory. 

<br/>
<br/>

## Installation

TL; DR; version:  

**Just include headers and:**

* define ```RCDB_MYSQL``` for MySQL,  ```RCDB_SQLITE``` for SQLite
* Ensure libs and headers are included. 

Compile and run the simplest example for SQLite

```bash 
> gcc $RCDB_HOME/cpp/examples/simple.cpp -o simple -I$RCDB_HOME/cpp/include/ -std=c++11 -lstdc++ -lsqlite3 -DRCDB_SQLITE 

> ./simple sqlite:////path/to/db/rcdb.sqlite 10452
```

with MySQL support:
```
> gcc $RCDB_HOME/cpp/examples/simple.cpp -o simple -I$RCDB_HOME/cpp/include/ -std=c++11 -lstdc++ -DRCDB_MYSQL `mysql_config --libs --cflags --include`

> ./simple mysql://rcdb@hallddb.jlab.org/rcdb 10452
```

Combine both to have MySQL and SQLite working together

---

RCDB C++ API is a header only since 0.03. Which means there is no more librcdb and separate step for RCDB. 
That also means that MySQL and SQLite libraries should be linked to the application which includes RCDB headers. 

In order for your code to build ensure flags/configuration:

* There is at lease C++11 support enabled and stdc++ library linked. This means that probably minimum GCC version to be used is 4.8:
  
    ```-std=c++11 -lstdc++```

* For MySQL:

     * Define ```RCDB_MYSQL``` 
     * Add mysql-connector includes and libs. There is useful ```mysql_config``` script:

     ``` -DRCDB_MYSQL `mysql_config --libs --cflags --include` ```

* For SQLite:

     * Define ```RCDB_SQLITE```:
     * Link libsqlite3 

     ``` -DRCDB_SQLITE -lsqlite3 ```


** Defining RCDB_MYSQL or RCDB_SQLITE **


​* Code ```#define RCDB_MYSQL```
* Compiler arguments ```-DRCDB_MYSQL```
* Scons ```env.Append(CPPDEFINES=['RCDB_MYSQL', 'RCDB_SQLITE'])```
* CMAKE ```add_definitions(-DRCDB_MYSQL)```
* SMBS ```AddRcdb()``` in SConscript


### Dependencies

#### Ubuntu

* MySQL ```libmysqlclient-dev``` or ```libmariadbclient-dev```
* SQLite ```libsqlite3-dev```

```sudo apt-get install libmariadbclient-dev libsqlite3-dev -y```

#### CentOS/Fedora

... please add, somebody ...

<br/>
<br/>

## Getting values

The example shows how to get values from RCDB:

```cpp
// Connect
Connection con("mysql://rcdb@hallddb/rcdb");

// Get event_count for run 10173
auto cnd = prov.GetCondition(10173, "event_count");

// Check event_count has a value for the run
if(!cnd) {
   std::cout<< "event_count condition is not set for the run"<<std::endl;
   return;
}

// Get value!
event_count = cnd->ToInt();
```

Here is the list of condition ToXXX functions and what values they are for:

```cpp
int ToInt();                           /// For int values
bool ToBool();                         /// For bool or int in DB
double ToDouble();                     /// For Double or int in DB
std::string ToString();                /// For Json, String or Blob
time_point<system_clock> ToTime();     /// For time value
rapidjson::Document ToJsonDocument();  /// For JSon document

rcdb::ValueTypes GetValueType();       /// Returns the type enum
```

## Examples

Examples are located in [$RCDB_HOME/cpp/examples](https://github.com/JeffersonLab/rcdb/tree/master/cpp/examples) folder. To build them use `with-examples=true` scons flag:

```bash
cd $RCDB_HOME/cpp
scons with-examples=true #...
```

After examples are built they are located in `$RCDB_HOME/cpp/bin` directory named as `exmpl_<...>`

<br>

**List of examples:**

* [simple.cpp](https://github.com/JeffersonLab/rcdb/blob/master/cpp/examples/simple.cpp) - Simple condition readout
* [get_trigger_params.cpp](https://github.com/JeffersonLab/rcdb/blob/master/cpp/examples/get_trigger_params.cpp) - Versatile data readout example. It includes:  
     * Reading conditions
     * Working with JSON serialized objects
     * Getting RCDB stored files contents
     * Working with config file parser
* [write_conditions.cpp](https://github.com/JeffersonLab/rcdb/blob/master/cpp/examples/write_conditions.cpp) - Writing conditions to RCDB from C++. It includes:  
     * Using WriteConnection
     * Adding condition values of different types




