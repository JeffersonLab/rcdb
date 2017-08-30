#(!) this CMake build system IS experimental and is made mostly for using CLion IDE.
# Scons - is the main RCDB make system, so please use it in order to build rcdb.lib and examples

cmake_minimum_required(VERSION 3.4)
project(rcdb_cpp)

option(WITH_MYSQL "Compile with MySQL support" OFF)
option(WITH_SQLITE "Compile with SQLite support" ON)


# Location of additional CMake modules
SET(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake/")

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -g -O0")

include_directories(include)

set(DB_REQIRED_LIBRARIES dl pthread)

# add SQLite related source files
set(SQLITE_SOURCE_FILES

        src/SQLiteCpp/Column.cpp
        src/SQLiteCpp/Database.cpp
        src/SQLiteCpp/Statement.cpp
        src/SQLiteCpp/Transaction.cpp
        src/SQLiteCpp/Exception.cpp

        include/SQLiteCpp/Assertion.h
        include/SQLiteCpp/Column.h
        include/SQLiteCpp/Database.h
        include/SQLiteCpp/Exception.h
        include/SQLiteCpp/SQLiteCpp.h
        include/SQLiteCpp/Statement.h
        include/SQLiteCpp/Transaction.h

        include/SQLite/sqlite3.h
        src/SQLite/sqlite3.c
        )

set(SOURCE_FILES
        ${SQLITE_SOURCE_FILES}

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

        tests/test_Connection.cpp
        tests/test_ConditionType.cpp
        tests/test_ConfigParser.cpp

        include/json/json.hpp

        tests/catch.hpp
        tests/catch.cpp
        )

if (WITH_MYSQL)
    add_definitions(-DRCDB_MYSQL)
    SET(TEST_SOURCE_FILES
            ${TEST_SOURCE_FILES}
            tests/test_MySqlProvider.cpp
            )
    include_directories(/usr/include/mysql)
    set(DB_REQIRED_LIBRARIES mysqlclient ${DB_REQIRED_LIBRARIES})

endif ()


if (WITH_SQLITE)

    #add_definitions(-DSQLITE_USE_LEGACY_STRUCT)
        #add_definitions(-DSQLITE_INT64_TYPE)
        #add_definitions(-DSQLITE_UINT64_TYPE)
    add_definitions(-DRCDB_SQLITE)
    include_directories(include/SQLite)
    include_directories(include/SQLiteCpp)
    set(DB_REQIRED_LIBRARIES sqlite3 ${DB_REQIRED_LIBRARIES})

    SET(TEST_SOURCE_FILES
            ${TEST_SOURCE_FILES}

            tests/test_SqLiteProvider.cpp
            )

    MESSAGE(STATUS "SOURCES:" ${SOURCE_FILES})
    MESSAGE(STATUS "TEST_SOURCE_FILES:" ${TEST_SOURCE_FILES})
endif ()

MESSAGE(STATUS "WITH_MYSQL  " ${WITH_MYSQL})
MESSAGE(STATUS "WITH_SQLITE " ${WITH_SQLITE})

add_executable(test_rcdb_cpp ${TEST_SOURCE_FILES})

add_executable(examples_trigger_params examples/get_trigger_params.cpp)
add_executable(examples_fadc_masks examples/get_fadc_masks.cpp)
add_executable(examples_write_conditions examples/write_conditions.cpp)
add_executable(examples_write_array_to_json examples/write_array_to_json.cpp)
add_executable(examples_write_objects_to_json examples/write_objects_to_json.cpp)

target_link_libraries(test_rcdb_cpp ${DB_REQIRED_LIBRARIES} dl pthread)
target_link_libraries(examples_trigger_params ${DB_REQIRED_LIBRARIES} dl pthread)
target_link_libraries(examples_fadc_masks ${DB_REQIRED_LIBRARIES} dl pthread)
target_link_libraries(examples_write_conditions ${DB_REQIRED_LIBRARIES} dl pthread)
target_link_libraries(examples_write_array_to_json ${DB_REQIRED_LIBRARIES} dl pthread)
target_link_libraries(examples_write_objects_to_json ${DB_REQIRED_LIBRARIES} dl pthread)