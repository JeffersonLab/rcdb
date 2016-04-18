#This CMakeList.txt file is in order

cmake_minimum_required(VERSION 3.4)
project(rcdb_cpp)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

include_directories(include)
include_directories(include/SQLite)

set(SOURCE_FILES
        src/SQLite/sqlite3.c
        src/SQLiteCpp/Backup.cpp
        src/SQLiteCpp/Column.cpp
        src/SQLiteCpp/Database.cpp
        src/SQLiteCpp/Statement.cpp
        src/SQLiteCpp/Transaction.cpp

        tests/catch.hpp
        tests/catch.cpp
        include/RCDB/ConditionType.h
        tests/test_ConditionType.cpp
        include/RCDB/MySqlProvider.h
        tests/test_MySqlProvider.cpp
        include/RCDB/SqLiteProvider.h
        tests/test_SqLiteProvider.cpp
        include/RCDB/DataProvider.h include/RCDB/Condition.h include/RCDB/Exceptions.h include/RCDB/MySqlConnectionInfo.h include/RCDB/Connection.h tests/test_Connection.cpp)

add_executable(test_rcdb_cpp ${SOURCE_FILES})
add_executable(examples_rcdb_cpp ${SOURCE_FILES} examples/simple.cpp)
target_link_libraries(test_rcdb_cpp mysqlclient dl pthread)
target_link_libraries(examples_rcdb_cpp mysqlclient dl pthread)