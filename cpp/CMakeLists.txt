# RCDB C++ is a header-only library - nothing here is required to USE it (just #include the headers
# and link sqlite3 and/or the mysql client). This CMake project builds the unit tests and examples.
#
# Build & run the SQLite unit tests:
#   cmake -S . -B build -DWITH_SQLITE=ON -DWITH_MYSQL=OFF
#   cmake --build build --target test_rcdb_cpp
#   RCDB_TEST_CONNECTION="sqlite:///<path-to>.sqlite" ./build/test_rcdb_cpp
# Create the test database with:  rcdb -c sqlite:///<path-to>.sqlite db init --add-cpp-tests --confirm

cmake_minimum_required(VERSION 3.5)
project(rcdb_cpp)

option(WITH_MYSQL  "Compile with MySQL support" OFF)
option(WITH_SQLITE "Compile with SQLite support" ON)


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
    include_directories(include/SQLiteCpp)
    set(DB_REQIRED_LIBRARIES sqlite3 ${DB_REQIRED_LIBRARIES})
endif()

MESSAGE(STATUS "WITH_MYSQL  " ${WITH_MYSQL})
MESSAGE(STATUS "WITH_SQLITE " ${WITH_SQLITE})


set(SOURCE_FILES
        /usr/include/sqlite3.h
        include/RCDB/SQLiteCpp.h
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
        ${SOURCE_FILES}

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

        tests/test_ConditionType.cpp

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

# The Connection and SqLiteProvider tests both pull in the SQLiteCpp amalgamation,
# whose out-of-line definitions are not `inline`. Compile them as a single unity
# translation unit (tests/test_sqlite_unity.cpp) so the definitions appear once.
if(WITH_SQLITE)
    list(APPEND TEST_SOURCE_FILES tests/test_sqlite_unity.cpp)
endif()

add_executable(test_rcdb_cpp ${TEST_SOURCE_FILES})
add_executable(examples_simple            examples/simple.cpp)
add_executable(examples_trigger_params    examples/get_trigger_params.cpp)
add_executable(examples_fadc_masks        examples/get_fadc_masks.cpp)
add_executable(examples_write_conditions  examples/write_conditions.cpp)
add_executable(examples_write_array_to_json examples/write_array_to_json.cpp)
add_executable(examples_write_objects_to_json examples/write_objects_to_json.cpp)

target_link_libraries(test_rcdb_cpp ${DB_REQIRED_LIBRARIES} dl pthread sqlite3)
target_link_libraries(examples_trigger_params ${DB_REQIRED_LIBRARIES} dl pthread)
target_link_libraries(examples_simple            ${DB_REQIRED_LIBRARIES} dl pthread)
target_link_libraries(examples_fadc_masks ${DB_REQIRED_LIBRARIES} dl pthread)
target_link_libraries(examples_write_conditions ${DB_REQIRED_LIBRARIES} dl pthread)
target_link_libraries(examples_write_array_to_json ${DB_REQIRED_LIBRARIES} dl pthread)
target_link_libraries(examples_write_objects_to_json ${DB_REQIRED_LIBRARIES} dl pthread)