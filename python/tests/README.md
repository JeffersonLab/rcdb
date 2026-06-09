# RCDB tests

## Python unit tests

The Python suite runs against an in-memory SQLite database - no setup, no
external server. From the `python/` directory:

```bash
python -m unittest discover -s tests -t tests
```

Each test creates its own schema in `setUp` via
`rcdb.provider.destroy_all_create_schema`, so the tests are fully hermetic.

This is what GitHub CI runs (`.github/workflows/python-tests.yml`) across
Python 3.9 - 3.13.

## C++ tests

The C++ Catch tests (`cpp/tests/`) need a SQLite database to read from. Create
one with the `rcdb` CLI - the canonical way to initialize an RCDB database -
using the `--add-cpp-tests` flag to seed the fixture the tests expect
(run 1 `int_cnd = 5`, etc.):

```bash
rcdb -c sqlite:///cpp_test.sqlite db init --add-cpp-tests --confirm
```

Then build and run the tests, pointing `RCDB_TEST_CONNECTION` at that database:

```bash
cd ../cpp
cmake -S . -B build -DWITH_SQLITE=ON -DWITH_MYSQL=OFF
cmake --build build --target test_rcdb_cpp
RCDB_TEST_CONNECTION="sqlite:///../cpp_test.sqlite" ./build/test_rcdb_cpp
```

GitHub CI does exactly this in `.github/workflows/cpp-tests.yml`.

## Seeding a database with generic test data

`rcdb db init` also accepts `--add-tests`, which seeds the generic
condition-type dataset (`a`-`g`) used by `test_select_values.py`. This is handy
for poking at a real SQLite file by hand:

```bash
rcdb -c sqlite:///my_test.sqlite db init --add-tests --confirm
```

The seeding logic for both flags lives in `rcdb/cli/test_data.py`.
