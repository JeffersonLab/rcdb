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

Both creating schema for the first time for a fresh database or updating the existing schema is done with
[Alembic](https://pypi.python.org/pypi/alembic)

Just run:

```bash
cd $RCDB_HOME
./alembic_rcdb upgrade head
```

> Since there where problems with installing alembic on some machines in counting house RCDB ships a copy of it within itself; `alembic_rcdb` command runs this embedded alembic version. 



