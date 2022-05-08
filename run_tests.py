import os
import unittest
import inspect
import subprocess
import sys
from unittest import TestSuite

this_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
python_folder = os.path.join(this_folder, "python")
python_tests_folder = os.path.join(python_folder, "tests")
cpp_folder = os.path.join(this_folder, "cpp")
cpp_bin_folder = os.path.join(cpp_folder, "bin")
cpp_test_executable = os.path.join(cpp_bin_folder, "rcdb_test_cpp")


# This is for travis
sys.path.append(python_folder)


def load_tests(loader, tests, pattern):
    test_suits = loader.discover(python_tests_folder)
    for test_suit in test_suits:
        assert isinstance(test_suit, TestSuite)
        unittest.TextTestRunner(verbosity=2).run(test_suit)


if __name__ == "__main__":
    result = unittest.main(exit=True)
    if not result.result.wasSuccessful():
        print("ERROR. Python tests are not passed")
        exit(1)

    print("\nRunning C++ tests with SQLite")
    sqlite_con_str = "sqlite:///" + os.path.join(python_tests_folder, 'test.sqlite.db')
    try:
        result = subprocess.call([cpp_test_executable], env=dict(os.environ, RCDB_TEST_CONNECTION=sqlite_con_str))
        if result:
            print("ERROR. C++ tests failed with SQLite")

        print("Running C++ tests with MySQL")
        if "RCDB_MYSQL_TEST_CONNECTION" not in os.environ:
            print("Set RCDB_MYSQL_TEST_CONNECTION environment variable pointing to TEST mysql database")
            print("Read https://github.com/JeffersonLab/rcdb/wiki/Development for more details")
            exit(1)

        mysql_con_str = os.environ["RCDB_MYSQL_TEST_CONNECTION"]
        result = subprocess.call([cpp_test_executable], env=dict(os.environ, RCDB_TEST_CONNECTION=mysql_con_str))

        if result:
            print("ERROR. C++ tests failed with MySQL")
    except OSError as e:
        print("ERROR. C++ tests file is not fount. Did one compiled it?")
        print("THE EXACT ERROR:", e)
