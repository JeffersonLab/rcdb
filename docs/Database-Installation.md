## Prerequisites  
> Evironment variables have to be set.  
    TL;DR; run `environment.*` script located in the RCDB root dir([more details](Installation)).  
    `RCDB_CONNECTION` must also be set (see below). 

Lets assume that one wants to install RCDB to the following database:

* database location: `localhost`
* database name: `rcdb`
* database user name: `rcdb`
* database user password: `password` 

then the connection string is

```
mysql://rcdb:password@localhost/rcdb
```

and ```RCDB_CONNECTION``` must be: 

```bash
export RCDB_CONNECTION='mysql://rcdb:password@localhost/rcdb'
```

## Create MySQL database  
(RCDB is tested for MySQL and MariaDB. Also RCDB should work with other MySQL forks while it hasn't been tested)
 
1. Create DB(aka schema) and a user with privileges:

    ```bash    
    mysql -u root -p
    ```

    > note, that root privileges are required to run ```mysql - u root ...``` for MariaDB by default. Run something like `sudo mysql -u root -p` for MariaDB

    ```sql
    CREATE SCHEMA rcdb;
    CREATE USER 'rcdb'@'localhost' IDENTIFIED BY 'password';
    GRANT ALL PRIVILEGES ON rcdb.* TO 'rcdb'@'localhost';
    ```

## Create or update DB structure

The command to create DB structure is: 

```bash
rcdb -c sqlite:///test.sqlite db init --drop-all

# For CI automation purposes --confirm flag can be added, but is discouraged for other cases  
```



The command to upgrade DB structure from previous RCDB versions:

```bash
rcdb -c sqlite:///test.sqlite db upgrade
```

