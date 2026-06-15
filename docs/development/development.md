# Development

RCDB Git is available at: 

https://github.com/JeffersonLab/rcdb


## Running the tests

The Python unit tests run against an in-memory SQLite database - no server or
fixture setup required. From the `python/` directory:

```bash
python -m unittest discover -s tests -t tests
```

The C++ Catch tests need a SQLite database. Create it with the `rcdb` CLI - the
canonical way to initialize an RCDB database - and seed the C++ fixture with
`--add-cpp-tests`, then point `RCDB_TEST_CONNECTION` at it:

```bash
rcdb -c sqlite:///cpp_test.sqlite db init --add-cpp-tests --confirm
cd $RCDB_HOME/cpp
cmake -S . -B build -DWITH_SQLITE=ON -DWITH_MYSQL=OFF
cmake --build build --target test_rcdb_cpp
RCDB_TEST_CONNECTION="sqlite:///../cpp_test.sqlite" ./build/test_rcdb_cpp
```

Both suites run on GitHub CI (`.github/workflows/python-tests.yml` and
`cpp-tests.yml`). See [python/tests/README.md](https://github.com/JeffersonLab/rcdb/blob/main/python/tests/README.md)
for more detail.


## Linting (pyflakes)

The Python sources are kept **pyflakes-clean**. Pyflakes catches unused imports,
undefined names, dead local variables and `str.format`/f-string mistakes.

`pyflakes` ships in the project's `dev` optional-dependency group. From the
`python/` directory:

```bash
# one-off, without installing the dev group into your environment:
uv run --extra dev pyflakes rcdb daq halld_rcdb tests utilities examples

# or, if you installed the project with the dev extra (pip install -e ".[dev]"):
pyflakes rcdb daq halld_rcdb tests utilities examples
```

The command must print nothing and exit `0`. This is a **mandatory CI gate**
(`.github/workflows/lint-pyflakes.yml`): any finding fails the build, so run it
before pushing.

A couple of conventions keep it clean without `# noqa` suppressions:

- **Intentional re-exports** (e.g. `rcdb/__init__.py`,
  `rcdb/web/modules/__init__.py`) use explicit imports plus an `__all__` list
  instead of relying on `import *`.
- Prefer explicit imports over `from module import *` so undefined-name checks
  keep working.


## Multi-Database Selector

The web interface supports switching between multiple databases from the browser.
See [Database Selector](website/database-selector.md) for configuration details.


## Publishing on pypi

```bash
uv build
uv run twine upload dist/*
```

[documentation.md](documentation.md ':include')


----------------------  
### Setup environment manually

If one needs to setup environment variables ***manually***, here is the list of variables, `environment.XXX` scripts set:

* `RCDB_HOME` - set to the rcdb directory (where environment.* scripts are located)
* `PYTHONPATH` - add `$RCDB_HOME/python`
* `PATH` -  add `"$RCDB_HOME":"$RCDB_HOME/bin":"$RCDB_HOME/cpp/bin":$PATH`

If one wants to use C++ ***readout*** API
* `LD_LIBRARY_PATH` - add `$RCDB_HOME/cpp/lib`