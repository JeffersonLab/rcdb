# CMake project for the RCDB C++ tests and examples.
#
# SQLiteCpp is fetched automatically (pinned by SQLITECPP_FETCH_TAG). To build against an
# already-installed copy instead, pass its location: -DSQLiteCpp_ROOT=/install/prefix
#
# Build & run the SQLite unit tests:
#   cmake -S . -B build -DWITH_SQLITE=ON -DWITH_MYSQL=OFF
#   cmake --build build --target test_rcdb_cpp
#   RCDB_TEST_CONNECTION="sqlite:///<path-to>.sqlite" ./build/test_rcdb_cpp
# Create the test database with:  rcdb -c sqlite:///<path-to>.sqlite db init --add-cpp-tests --confirm

cmake_minimum_required(VERSION 3.14)   # FetchContent_MakeAvailable
project(rcdb_cpp)

option(WITH_MYSQL  "Compile with MySQL support" OFF)
option(WITH_SQLITE "Compile with SQLite support" ON)

set(SQLITECPP_FETCH_TAG "3.3.3" CACHE STRING "SQLiteCpp git tag to fetch (used unless -DSQLiteCpp_ROOT is given)")

# Location of additional CMake modules
SET(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake/")

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -g -O0")

include_directories(include)

set(DB_REQIRED_LIBRARIES dl pthread)

if(WITH_MYSQL)
    add_definitions(-DRCDB_MYSQL)
    include_directories(/usr/include/mysql)
    set(DB_REQIRED_LIBRARIES mysqlclient ${DB_REQIRED_LIBRARIES})
endif()

if(WITH_SQLITE)
    add_definitions(-DRCDB_SQLITE)

    # Fetch a known-good SQLiteCpp by default. If the user points CMake at an existing
    # install (-DSQLiteCpp_ROOT=/prefix, CMake's standard package-location hint), use that.
    if(SQLiteCpp_ROOT)
        find_package(SQLiteCpp CONFIG REQUIRED)
        message(STATUS "Using SQLiteCpp from ${SQLiteCpp_ROOT}")
    else()
        message(STATUS "Fetching SQLiteCpp ${SQLITECPP_FETCH_TAG}")
        include(FetchContent)
        # By default SQLiteCpp compiles its own bundled SQLite3 amalgamation. We forward
        # this knob (keeping SQLiteCpp's own default, ON) so it can be turned off to link
        # the platform's libsqlite3 instead: -DSQLITECPP_INTERNAL_SQLITE=OFF
        set(SQLITECPP_INTERNAL_SQLITE ON CACHE BOOL "Compile SQLiteCpp's bundled SQLite3 (OFF links system libsqlite3)")
        set(SQLITECPP_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
        set(SQLITECPP_BUILD_TESTS    OFF CACHE BOOL "" FORCE)
        set(SQLITECPP_RUN_CPPLINT    OFF CACHE BOOL "" FORCE)
        set(SQLITECPP_RUN_CPPCHECK   OFF CACHE BOOL "" FORCE)
        FetchContent_Declare(SQLiteCpp
                GIT_REPOSITORY https://github.com/SRombauts/SQLiteCpp.git
                GIT_TAG        ${SQLITECPP_FETCH_TAG})
        FetchContent_MakeAvailable(SQLiteCpp)
    endif()

    # The SQLiteCpp target carries its own sqlite3 dependency and include dirs
    # (transitively exposing <sqlite3.h>), so we do not link a separate sqlite3.
    set(DB_REQIRED_LIBRARIES SQLiteCpp ${DB_REQIRED_LIBRARIES})
endif()

MESSAGE(STATUS "WITH_MYSQL  " ${WITH_MYSQL})
MESSAGE(STATUS "WITH_SQLITE " ${WITH_SQLITE})

set(RCDB_HEADERS
        include/RCDB/ConditionType.h
        include/RCDB/MySqlProvider.h
        include/RCDB/SqLiteProvider.h
        include/RCDB/DataProvider.h
        include/RCDB/Condition.h
        include/RCDB/Exceptions.h
        include/RCDB/MySqlConnectionInfo.h
        include/RCDB/Connection.h
        include/RCDB/StringUtils.h
        include/RCDB/ConfigParser.h
        include/RCDB/RcdbFile.h
        )

SET(TEST_SOURCE_FILES
        ${RCDB_HEADERS}

        tests/test_ConditionType.cpp
        tests/test_Condition.cpp

        tests/catch.hpp
        tests/catch.cpp
        tests/test_ConfigParser.cpp
        include/json/json.hpp
        )

# Provider tests are gated by the corresponding DB backend, so an SQLite-only
# build does not need MySQL headers (mysql.h) and a MySQL-only build does not need SQLite.
if(WITH_MYSQL)
    list(APPEND TEST_SOURCE_FILES tests/test_MySqlProvider.cpp)
endif()

if(WITH_SQLITE)
    list(APPEND TEST_SOURCE_FILES tests/test_SqLiteProvider.cpp tests/test_Connection.cpp)
endif()

# Read examples and tests build with either backend (SQLite is the default).
add_executable(test_rcdb_cpp ${TEST_SOURCE_FILES})
add_executable(examples_simple            examples/simple.cpp)
add_executable(examples_trigger_params    examples/get_trigger_params.cpp)
add_executable(examples_fadc_masks        examples/get_fadc_masks.cpp)

target_link_libraries(test_rcdb_cpp ${DB_REQIRED_LIBRARIES})
target_link_libraries(examples_trigger_params ${DB_REQIRED_LIBRARIES})
target_link_libraries(examples_simple         ${DB_REQIRED_LIBRARIES})
target_link_libraries(examples_fadc_masks ${DB_REQIRED_LIBRARIES})

# Writing to RCDB from C++ goes through WritingConnection, which is MySQL-only
# (the SQLite provider is read-only). So the write examples are built only when
# MySQL support is enabled.
if(WITH_MYSQL)
    add_executable(examples_write_conditions  examples/write_conditions.cpp)
    add_executable(examples_write_array_to_json examples/write_array_to_json.cpp)
    add_executable(examples_write_objects_to_json examples/write_objects_to_json.cpp)

    target_link_libraries(examples_write_conditions ${DB_REQIRED_LIBRARIES})
    target_link_libraries(examples_write_array_to_json ${DB_REQIRED_LIBRARIES})
    target_link_libraries(examples_write_objects_to_json ${DB_REQIRED_LIBRARIES})
endif()
