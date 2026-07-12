- [Installation](Cpp#installation)  
- [Getting values](Cpp#getting-values)  
- [Examples](Cpp#examples)

## RCDB C++ API overview

C++ API is a header only library that allows to read RCDB condition values for the run. The library doesn't provide possibility of run selection queries at this point. Also it requires C++11 to compile. 

C++ API code is located in [$RCDB_HOME/cpp](https://github.com/JeffersonLab/rcdb/tree/main/cpp) directory. 

<br/>
<br/>

## Installation

### Quick reference

Build with CMake from `$RCDB_HOME/cpp`. Default configure line:

```bash
cmake -S . -B build -DWITH_SQLITE=ON -DWITH_MYSQL=OFF
cmake --build build
```

**CMake options**

| Option | Default | Description |
|--------|---------|-------------|
| `WITH_SQLITE` | `ON` | Build the SQLite backend (read-only). |
| `WITH_MYSQL` | `OFF` | Build the MySQL/MariaDB backend (read + write). |
| `SQLiteCpp_ROOT` | *(unset)* | Install prefix of an existing SQLiteCpp. If set, that install is used instead of fetching one. |
| `SQLITECPP_FETCH_TAG` | `3.3.3` | SQLiteCpp git tag fetched with `FetchContent` (used unless `SQLiteCpp_ROOT` is given). |
| `SQLITECPP_INTERNAL_SQLITE` | `ON` | When fetching SQLiteCpp: `ON` compiles its bundled SQLite3; `OFF` links the system `libsqlite3`. Forwarded to SQLiteCpp with its own default. |

**Dependencies** (backend-dependent, system-independent)

| Dependency | Needed for | How provided                                     |
|------------|-----------|--------------------------------------------------|
| C++11 , CMake ≥ 3.14 | always | system                                           |
| [SQLiteCpp](https://github.com/SRombauts/SQLiteCpp) ≥ 3.x | `WITH_SQLITE` | auto-fetched, or use `-DSQLiteCpp_ROOT`          |
| SQLite3 C library | `WITH_SQLITE` | comes with SQLiteCpp (or system `libsqlite3`)    |
| MySQL/MariaDB client | `WITH_MYSQL` | system package (`libmysqlclient` / `libmariadb`) |
| `pthread`, `dl` | always | system                                           |

RCDB's own headers are header-only; the database backends above are the only things you link.
Read on for OS-specific package names and full build/run instructions.

<br/>

RCDB's own C++ code is **header-only** — you just `#include` the headers. The database
backends are external libraries you link against:

* **SQLite backend** → the [SQLiteCpp](https://github.com/SRombauts/SQLiteCpp) library
  (RCDB no longer vendors its own copy — see below).
* **MySQL backend** → the MySQL/MariaDB client library.

The CMake project in `$RCDB_HOME/cpp` builds the unit tests and examples and handles
compiler flags and library linkage for you.

### SQLiteCpp dependency

The SQLite backend uses [SQLiteCpp](https://github.com/SRombauts/SQLiteCpp), resolved
in one of two ways:

1. **Fetched automatically** (default). CMake pulls the pinned tag (`SQLITECPP_FETCH_TAG`,
   default `3.3.3`) with `FetchContent` and builds it as part of the project. Override the
   tag with `-DSQLITECPP_FETCH_TAG=<git-tag>`.

   By default the fetched SQLiteCpp compiles its own bundled SQLite3 (SQLiteCpp's default).
   To link the platform's SQLite instead — e.g. to share one SQLite with the rest of your
   software stack — pass `-DSQLITECPP_INTERNAL_SQLITE=OFF` (needs `libsqlite3` dev headers).

2. **An existing install**, by pointing CMake at its prefix (used when your environment
   already provides SQLiteCpp, e.g. gluex):

   ```bash
   cmake -S . -B build -DSQLiteCpp_ROOT=/install/prefix
   ```

> For consumers that do **not** use CMake (such as `halld_recon`): make your build's
> SQLiteCpp headers (`<SQLiteCpp/SQLiteCpp.h>`) and library visible the same way you do
> for any other dependency. RCDB includes SQLiteCpp headers by their canonical
> `<SQLiteCpp/SQLiteCpp.h>` path and does not bundle its own copy.

### Dependencies

#### Ubuntu / Debian

```bash
# SQLite (the C library; SQLiteCpp is fetched or provided via -DSQLiteCpp_ROOT)
sudo apt-get install libsqlite3-dev

# MySQL (either one)
sudo apt-get install libmysqlclient-dev
# or
sudo apt-get install libmariadbclient-dev
```

#### CentOS / Fedora

```bash
sudo dnf install sqlite-devel mysql-devel
```

### SQLite only

```bash
cd $RCDB_HOME/cpp
cmake -S . -B build -DWITH_SQLITE=ON -DWITH_MYSQL=OFF
cmake --build build --target examples_simple

./build/examples_simple sqlite:////path/to/db/rcdb.sqlite 10452
```

> Add `-DSQLiteCpp_ROOT=/install/prefix` to reuse an existing SQLiteCpp
> instead of fetching one.

### MySQL only

```bash
cd $RCDB_HOME/cpp
cmake -S . -B build -DWITH_SQLITE=OFF -DWITH_MYSQL=ON
cmake --build build --target examples_simple

./build/examples_simple mysql://rcdb@hallddb.jlab.org/rcdb 10452
```

### MySQL + SQLite (both)

```bash
cd $RCDB_HOME/cpp
cmake -S . -B build -DWITH_SQLITE=ON -DWITH_MYSQL=ON
cmake --build build --target examples_simple

# use either connection string:
./build/examples_simple sqlite:////path/to/db/rcdb.sqlite 10452
./build/examples_simple mysql://rcdb@hallddb.jlab.org/rcdb 10452
```

> CMake sets the required compile definitions (`-DRCDB_SQLITE`, `-DRCDB_MYSQL`) and links
> the correct libraries automatically based on the `-DWITH_*` options.

<br/>
<br/>

## Getting values

The example shows how to get values from RCDB:

```cpp
// Connect
Connection con("mysql://rcdb@hallddb/rcdb");

// Get event_count for run 10173
auto cnd = con.GetCondition(10173, "event_count");

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
tao::json::value ToJsonDocument();     /// For Json values: parsed JSON document
rcdb::ValueTypes GetValueType();       /// Returns the type enum
```

> **Note on `ToJsonDocument()`:** it now returns a `tao::json::value` (the bundled
> [taocpp/json](https://github.com/taocpp/json) library) instead of a
> `rapidjson::Document` — rapidjson has been removed so the public headers no longer
> pull it in. The parsed structure/values are identical; only the accessor API changes,
> e.g. `json.at("%(config)").get_string()` (tao) instead of
> `json["%(config)"].GetString()` (rapidjson). It throws `rcdb::ValueFormatError` if the
> value type is not Json or the text is not valid JSON. You can also use `ToString()` and
> parse with your own library.

## Building the tests and examples (CMake)

The C++ tests and examples are built with CMake. SQLite-only is the default; add
`-DWITH_MYSQL=ON` to also build the MySQL provider (needs `libmysqlclient-dev`).

```bash
cd $RCDB_HOME/cpp
cmake -S . -B build -DWITH_SQLITE=ON -DWITH_MYSQL=OFF
cmake --build build --target test_rcdb_cpp        # unit tests
cmake --build build                               # everything, incl. examples
```

The unit tests need a SQLite database with test data. Create one with the `rcdb` CLI
and point `RCDB_TEST_CONNECTION` at it:

```bash
rcdb -c sqlite:///cpp_test.sqlite db init --add-cpp-tests --confirm
RCDB_TEST_CONNECTION="sqlite:///cpp_test.sqlite" ./build/test_rcdb_cpp
```

Examples are located in the [$RCDB_HOME/cpp/examples](https://github.com/JeffersonLab/rcdb/tree/main/cpp/examples) folder
and are built as the `examples_*` targets by the `cmake --build build` command above.

After examples are built they are located in the `cpp/build` directory, named after their CMake
targets (e.g. `examples_trigger_params`). There is no separate install step or custom output directory.

<br>

**List of examples:**

* [simple.cpp](https://github.com/JeffersonLab/rcdb/blob/main/cpp/examples/simple.cpp) (target `examples_simple`) - Simple condition readout. Used as the introductory build example in the Installation section above.
* [get_trigger_params.cpp](https://github.com/JeffersonLab/rcdb/blob/main/cpp/examples/get_trigger_params.cpp) (target `examples_trigger_params`) - Versatile data readout example. It includes:  
     * Reading conditions
     * Working with JSON serialized objects
     * Getting RCDB stored files contents
     * Working with config file parser
* [get_fadc_masks.cpp](https://github.com/JeffersonLab/rcdb/blob/main/cpp/examples/get_fadc_masks.cpp) (target `examples_fadc_masks`) - Reading FADC masks

Writing to RCDB from C++ goes through `WritingConnection`, which is **MySQL-only** (the
SQLite provider is read-only). The following write examples are therefore built only when
configured with `-DWITH_MYSQL=ON`:

* [write_conditions.cpp](https://github.com/JeffersonLab/rcdb/blob/main/cpp/examples/write_conditions.cpp) (target `examples_write_conditions`) - Writing conditions to RCDB from C++. It includes:  
     * Using WritingConnection
     * Adding condition values of different types
* [write_array_to_json.cpp](https://github.com/JeffersonLab/rcdb/blob/main/cpp/examples/write_array_to_json.cpp) (target `examples_write_array_to_json`) - Writing an array serialized to JSON
* [write_objects_to_json.cpp](https://github.com/JeffersonLab/rcdb/blob/main/cpp/examples/write_objects_to_json.cpp) (target `examples_write_objects_to_json`) - Writing objects serialized to JSON




