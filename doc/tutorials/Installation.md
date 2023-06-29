#### 0. Get rcdb

Clone this repository:

```
git clone https://github.com/JeffersonLab/rcdb.git
```

<br>  

#### 1. Install python requirements

```
cd rcdb
pip install -r requirements.txt
```


<br>  

#### 2. Set environment

There are *environment.\<your shell\>* scripts, which automatically set
environment variables for the of rcdb

```bash
source environment.bash   # for bash
```

The script sets ***$RCDB_HOME*** to RCDB root directory, appends ***$PYTHONPATH*** and ***$PATH***. The full list of variables set by the script and how to set them manually one can [read below](#setup-environment-manually). 

<br>  

#### 3. Database connection

One needs so called "connection string" in order to connect to database. For now we consider to use MySQL and SQLite databases. The connection strings for them are:

***MySQL***  
```
mysql://user_name:password@host:port/database
```


***SQLite***
```
sqlite:///path_to_file
```

**(!)** Note that because SQLite doesn't have user_name and password, it starts with three slashes ///.
And thus there should be four slashes //// in absolute path to file.

```
sqlite:////home/user_name/rcdb.sqlite.db
```

<br>  

***RCDB_CONNECTION***  

The common way of different parts of RCDB to know the connection string is to set RCDB_CONNECTION environment variable:

```bash
#bash: 
export RCDB_CONNECTION="mysql://rcdb@hallddb.jlab.org/rcdb"
```

The other common way is to set `-c \<connection string\>` key


<br>   

#### 4. Experimenting  

To experiment with RCDB and examples below, there is create_empty_sqlite.py script in $RCDB_HOME/python folder.
The script creates empty sqlite database. The usage is:

```bash
python $RCDB_HOME/python/create_empty_sqlite.py path_to_database.db
```

One can download HALLD sqlite database (autogenerated daily) here:

https://halldweb.jlab.org/dist/rcdb.sqlite

<br>
<br>
<br>

----------------------  
### Setup environment manually

If one needs to setup environment variables ***manually***, here is the list of variables, `environment.XXX` scripts set:

* `RCDB_HOME` - set to the rcdb directory (where environment.* scripts are located)
* `PYTHONPATH` - add `$RCDB_HOME/python` - in order to import rcdb module from python
* `PATH` -  add `"$RCDB_HOME":"$RCDB_HOME/bin":$PATH` 

If one wants to use C++ ***readout*** API
* `LD_LIBRARY_PATH` - add `$RCDB_HOME/cpp/lib` 
* `CPLUS_INCLUDE_PATH` - add `$RCDB_HOME/cpp/include` 
* `PATH` - add `"$RCDB_HOME/bin"`


