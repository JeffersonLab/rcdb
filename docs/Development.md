[documentation.md](../../JANA2/docs/development/documentation.md)# 1. Establishing integration tests

1. Create MySQL database for the test purposes

    ```bash
    mysql -u root -p
    ```

    ```mysql
    CREATE SCHEMA test_rcdb;
    CREATE USER 'test_rcdb'@'localhost' IDENTIFIED BY 'test_rcdb';
    GRANT ALL PRIVILEGES ON test_rcdb.* TO 'test_rcdb'@'localhost';
     ```

2. Set RCDB_MYSQL_TEST_CONNECTION environment variable

    ```bash
    export RCDB_MYSQL_TEST_CONNECTION="mysql://test_rcdb@localhost/test_rcdb"

    ```

3. run create_test_database.py

    ```bash
    python $RCDB_HOME/python/tests/create_test_database.py $RCDB_MYSQL_TEST_CONNECTION
    ```


4. Run ```test_all_rcdb```


## Publishing on pypi

```bash
python -m pip install build twine
python -m build
twine upload dist/*
```

[filename](documentation.md ':include')
