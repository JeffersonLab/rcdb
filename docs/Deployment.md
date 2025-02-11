Deploying RCDB MySQL database on local machine. 

### 0. Clone RCDB repo 

Here is a very brief instruction for it (for bash shell):

```bash
git clone https://github.com/JeffersonLab/rcdb.git
cd rcdb
source environment.bash

# now to check that everything works, test connect to HallD RCDB
export RCDB_CONNECTION=mysql://rcdb@hallddb.jlab.org/rcdb
rcnd
```

rcnd should answer something like:

```
Runs total: 10462
Last run  : 42387
Condition types total: 53
Conditions: 
<list of conditions>
```

More information is in [Installation chapter](https://github.com/JeffersonLab/rcdb/wiki/Installation)


### 1. Create MySQL database

```bash
mysql -u root -p
```

```mysql
CREATE SCHEMA rcdb;
CREATE USER 'rcdb'@'localhost';
GRANT ALL PRIVILEGES ON rcdb.* TO 'rcdb'@'localhost';
```

### 2. Create DB structure
And fill in a minimal set of common conditions. 

```bash 
python $RCDB_HOME/python/create_empty_db.py -c mysql://rcdb@localhost/rcdb --i-am-sure --add-def-con
```

The right answer should be:
```
creating database:
database created
default conditions filled
```

### 3. Testing the installation

Now check rcdn 

```
export RCDB_CONNECTION=mysql://rcdb@localhost/rcdb
rcnd
```

The output should be like:

```
Runs total: 0
Condition types total: 13
Conditions: 
<list of conditions>
```

Lets create a first run (run 1) and fill event_count=12345 for run 1

```bash
rcnd --new-run 1
rcnd --write 12345 --replace 1 event_count

#lets check conditions for run 1
rcnd 1
```

Output should be like:

```
event_count = 12345
```
More about rcnd command and command line tools one could find in 
[CLI basics chapter](https://github.com/JeffersonLab/rcdb/wiki/rcnd).

### 4. Test run the web site

```bash
python $RCDB_HOME/start_www.py
```

The output should be like:

```
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
* Restarting with reloader
```

Now follow to http://127.0.0.1:5000/ in the browser to see the site. 

