#!/bin/bash

# Get script directory
SCRIPT_PATH=$0:a:h;

#set our environment
export RCDB_HOME=$SCRIPT_PATH 
export LD_LIBRARY_PATH="$RCDB_HOME/cpp/lib":$LD_LIBRARY_PATH
export CPLUS_INCLUDE_PATH="$RCDB_HOME/cpp/include":$CPLUS_INCLUDE_PATH
export PYTHONPATH="$RCDB_HOME/python":$PYTHONPATH
export PATH="$RCDB_HOME":"$RCDB_HOME"/bin:"$RCDB_HOME"/cpp/bin:$PATH

